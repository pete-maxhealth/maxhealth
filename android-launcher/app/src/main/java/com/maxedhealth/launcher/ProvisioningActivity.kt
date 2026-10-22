package com.maxedhealth.launcher

import android.content.ActivityNotFoundException
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.Button
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Runs once, first launch only. On every subsequent launch, MainActivity is opened
 * directly (see the SharedPreferences check in onCreate below) — this activity's
 * whole job is to get from "just installed" to "server running, safe to skip this
 * screen forever after."
 *
 * Deliberately a plain step-by-step sequence rather than one big function, so each
 * step's on-screen text can say plainly what's happening and why, rather than the
 * user watching a spinner with no idea what step they're stuck on if something goes
 * wrong. Same reasoning as MaxedHealth's own debug traces — narrating what's
 * actually happening beats a generic loading state.
 */
class ProvisioningActivity : ComponentActivity() {

    private lateinit var prefs: SharedPreferences
    private lateinit var statusText: TextView
    private lateinit var actionButton: Button

    private val storagePermissionLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            proceedToStep(Step.REQUEST_NOTIFICATIONS)
        }

    private val notificationPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) {
            proceedToStep(Step.REQUEST_BATTERY_EXEMPTION)
        }

    // Termux only accepts commands from apps granted this runtime permission.
    // It was declared in the manifest but never actually asked for, so Termux
    // silently ignored the provisioning command (found on Pete's phone 23/09).
    private val termuxPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                proceedToStep(Step.BOOTSTRAP_INSTRUCTIONS)
            } else {
                statusText.text = "MaxedHealth needs permission to run commands in Termux - " +
                    "it's how everything gets set up without you typing anything. " +
                    "Tap below, then allow \"Run commands in Termux environment\"."
                actionButton.visibility = View.VISIBLE
                actionButton.text = "Open app settings"
                actionButton.setOnClickListener {
                    val details = Intent(
                        Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                        Uri.parse("package:$packageName")
                    )
                    tryLaunch(installReturnLauncher, details)
                }
            }
        }

    private val batteryExemptionLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            proceedToStep(Step.CHECK_TERMUX)
        }

    private val installReturnLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            // Comes back here whether or not the install actually completed — F-Droid
            // doesn't hand back a clean success/failure result, so re-run the same
            // check step rather than assuming either outcome.
            proceedToStep(currentStep)
        }

    /** Launches an intent, returning false instead of crashing if nothing on this phone can open it. */
    private fun tryLaunch(
        launcher: androidx.activity.result.ActivityResultLauncher<Intent>,
        intent: Intent
    ): Boolean = try {
        launcher.launch(intent)
        true
    } catch (e: ActivityNotFoundException) {
        false
    }

    private enum class Step {
        REQUEST_STORAGE, REQUEST_NOTIFICATIONS, REQUEST_BATTERY_EXEMPTION,
        CHECK_TERMUX, CHECK_TERMUX_BOOT, CHECK_TERMUX_API, REQUEST_TERMUX_PERMISSION,
        BOOTSTRAP_INSTRUCTIONS, WAITING_FOR_BOOTSTRAP,
        RUN_PROVISION_SCRIPT, WAITING_FOR_PROVISION, DONE
    }

    private var currentStep: Step = Step.REQUEST_STORAGE

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        prefs = getSharedPreferences("maxhealth_launcher", MODE_PRIVATE)

        if (prefs.getBoolean("provisioning_complete", false)) {
            startActivity(Intent(this, MainActivity::class.java))
            finish()
            return
        }

        setContentView(R.layout.activity_provisioning)
        statusText = findViewById(R.id.provisioningStatusText)
        actionButton = findViewById(R.id.provisioningActionButton)

        proceedToStep(Step.REQUEST_STORAGE)
    }

    /**
     * One entry point for every step, rather than each permission callback deciding
     * on its own what comes next — makes the actual ORDER of the flow visible in
     * one place (this function), not scattered across several callback lambdas.
     */
    private fun proceedToStep(step: Step) {
        currentStep = step
        actionButton.visibility = View.GONE  // each step that needs it shows it again
        when (step) {
            Step.REQUEST_STORAGE -> {
                statusText.text = "Setting up storage access…"
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    if (!android.os.Environment.isExternalStorageManager()) {
                        // The per-app screen needs "package:<name>" attached - without it,
                        // some phones (confirmed on Pete's HyperOS) have nothing to open
                        // and the app crashes. Falls back to the general All-files list,
                        // then to skipping the step, rather than ever crashing here.
                        val appScreen = Intent(
                            Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION,
                            Uri.parse("package:$packageName")
                        )
                        val listScreen = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                        if (!tryLaunch(storagePermissionLauncher, appScreen) &&
                            !tryLaunch(storagePermissionLauncher, listScreen)) {
                            proceedToStep(Step.REQUEST_NOTIFICATIONS)
                        }
                    } else {
                        proceedToStep(Step.REQUEST_NOTIFICATIONS)
                    }
                } else {
                    proceedToStep(Step.REQUEST_NOTIFICATIONS)
                }
            }

            Step.REQUEST_NOTIFICATIONS -> {
                statusText.text = "Enabling notifications…"
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    notificationPermissionLauncher.launch(android.Manifest.permission.POST_NOTIFICATIONS)
                } else {
                    proceedToStep(Step.REQUEST_BATTERY_EXEMPTION)
                }
            }

            Step.REQUEST_BATTERY_EXEMPTION -> {
                if (TermuxBridge.isIgnoringBatteryOptimizations(this)) {
                    // Already granted (Android remembers this permanently) — skip
                    // straight past without showing the system screen at all. This
                    // was firing on every single launch before, which is what made
                    // this step feel bolted-on rather than a real onboarding step.
                    proceedToStep(Step.CHECK_TERMUX)
                } else {
                    statusText.text = "Android will now ask to let MaxedHealth Sync run in the background. " +
                        "Please tap Allow — without it, phones tend to stop syncing overnight."
                    TermuxBridge.requestIgnoreBatteryOptimizations(this)
                    // No launcher wired to a specific result here on purpose — this
                    // dialog's result code isn't reliable across manufacturers, and the
                    // NEXT step (checking Termux) doesn't depend on this one having
                    // succeeded, so just move on rather than block on it.
                    proceedToStep(Step.CHECK_TERMUX)
                }
            }

            Step.CHECK_TERMUX -> {
                if (TermuxBridge.isTermuxInstalled(this)) {
                    proceedToStep(Step.CHECK_TERMUX_BOOT)
                } else {
                    statusText.text = "MaxedHealth needs Termux installed — tap below to install it, " +
                        "then come back here."
                    actionButton.visibility = View.VISIBLE
                    actionButton.text = "Install Termux"
                    actionButton.setOnClickListener {
                        if (!tryLaunch(installReturnLauncher, TermuxBridge.fdroidIntentFor("com.termux"))) {
                            statusText.text = "Couldn't open the download page. Install Termux from f-droid.org in your browser, then come back here."
                        }
                    }
                }
            }

            Step.CHECK_TERMUX_BOOT -> {
                if (TermuxBridge.isTermuxBootInstalled(this)) {
                    proceedToStep(Step.CHECK_TERMUX_API)
                } else {
                    statusText.text = "Almost there — one more small app needed (Termux:Boot, " +
                        "keeps things running after a phone restart)."
                    actionButton.visibility = View.VISIBLE
                    actionButton.text = "Install Termux:Boot"
                    actionButton.setOnClickListener {
                        if (!tryLaunch(installReturnLauncher, TermuxBridge.fdroidIntentFor("com.termux.boot"))) {
                            statusText.text = "Couldn't open the download page. Install Termux:Boot from f-droid.org in your browser, then come back here."
                        }
                    }
                }
            }

            Step.CHECK_TERMUX_API -> {
                if (TermuxBridge.isTermuxApiInstalled(this)) {
                    proceedToStep(Step.REQUEST_TERMUX_PERMISSION)
                } else {
                    statusText.text = "Last one — Termux:API, needed so MaxedHealth can talk to Termux."
                    actionButton.visibility = View.VISIBLE
                    actionButton.text = "Install Termux:API"
                    actionButton.setOnClickListener {
                        if (!tryLaunch(installReturnLauncher, TermuxBridge.fdroidIntentFor("com.termux.api"))) {
                            statusText.text = "Couldn't open the download page. Install Termux:API from f-droid.org in your browser, then come back here."
                        }
                    }
                }
            }

            Step.REQUEST_TERMUX_PERMISSION -> {
                val perm = "com.termux.permission.RUN_COMMAND"
                if (checkSelfPermission(perm) == PackageManager.PERMISSION_GRANTED) {
                    proceedToStep(Step.BOOTSTRAP_INSTRUCTIONS)
                } else {
                    statusText.text = "Allowing MaxedHealth to talk to Termux…"
                    termuxPermissionLauncher.launch(perm)
                }
            }

            Step.BOOTSTRAP_INSTRUCTIONS -> {
                statusText.text = "One last manual step, and it's the only one: " +
                    "we've copied a single line to your clipboard. Termux is about to open — " +
                    "just paste (long-press the screen → Paste) and press Enter. " +
                    "We'll take it from there automatically."
                actionButton.visibility = View.VISIBLE
                actionButton.text = "Open Termux"
                actionButton.setOnClickListener {
                    TermuxBridge.copyBootstrapCommandToClipboard(this)
                    TermuxBridge.launchTermux(this)
                    proceedToStep(Step.WAITING_FOR_BOOTSTRAP)
                }
            }

            Step.WAITING_FOR_BOOTSTRAP -> {
                statusText.text = "Waiting for that one line to be pasted and run in Termux…"
                actionButton.visibility = View.VISIBLE
                actionButton.text = "I've done it"
                actionButton.setOnClickListener {
                    // The button is a manual nudge for if polling seems stuck — the
                    // real detection is the poll loop below, which fires
                    // automatically the moment it sees allow-external-apps actually
                    // took effect, without needing this tap at all in the normal
                    // case.
                    pollForBootstrapCompletion()
                }
                pollForBootstrapCompletion()
            }

            Step.RUN_PROVISION_SCRIPT -> {
                statusText.text = "Setting everything up in the background — this can take a minute…"
                TermuxBridge.stageProvisionScript(this, assets.open("provision.sh").bufferedReader().readText())
                TermuxBridge.runProvisionScript(this)
                proceedToStep(Step.WAITING_FOR_PROVISION)
            }

            Step.WAITING_FOR_PROVISION -> pollForProvisionCompletion()

            Step.DONE -> {
                prefs.edit().putBoolean("provisioning_complete", true).apply()
                startActivity(Intent(this, MainActivity::class.java))
                finish()
            }
        }
    }

    /**
     * Polls for the sentinel file provision.sh's bootstrap check writes, rather
     * than trusting the intent fired cleanly — see TermuxBridge's class comment for
     * why this is the only reliable signal available to us.
     */
    private fun pollForBootstrapCompletion() {
        lifecycleScope.launch {
            // Can't fire RUN_COMMAND to test this yet — allow-external-apps being
            // true is exactly what we're waiting to confirm, so this has to be a
            // plain file check, not a RUN_COMMAND round-trip. The bootstrap command
            // itself (TermuxBridge.bootstrapCommand()) ends by touching this
            // sentinel file directly as its last step, once storage setup and the
            // properties change have both actually succeeded — not assumed.
            var attempts = 0
            while (attempts < 60) {
                if (TermuxBridge.sentinelFile("bootstrap").exists()) {
                    proceedToStep(Step.RUN_PROVISION_SCRIPT)
                    return@launch
                }
                delay(2000)
                attempts++
            }
            statusText.text = "Still waiting — if you've already pasted and pressed Enter, " +
                "tap \"I've done it\" above, or try reopening Termux and pasting again."
        }
    }

    private fun pollForProvisionCompletion() {
        lifecycleScope.launch {
            var attempts = 0
            while (attempts < 90) {
                if (TermuxBridge.sentinelFile("provision-complete").exists()) {
                    proceedToStep(Step.DONE)
                    return@launch
                }
                delay(2000)
                attempts++
            }
            statusText.text = "This is taking longer than expected. Check your internet " +
                "connection, then tap Retry."
            actionButton.visibility = View.VISIBLE
            actionButton.text = "Retry"
            actionButton.setOnClickListener { proceedToStep(Step.RUN_PROVISION_SCRIPT) }
        }
    }
}
