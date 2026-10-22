package com.maxedhealth.launcher

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import java.io.File

/**
 * Everything Termux-specific lives here, kept separate from the Activities so the
 * provisioning *flow* (in ProvisioningActivity) stays readable on its own.
 *
 * One constant worth keeping honest: `sentinel file appeared` is our ONLY reliable
 * signal that a RUN_COMMAND actually executed. We can't read Termux's own
 * process list or its private files, and Termux gives external callers no direct
 * success/failure callback for RUN_COMMAND (per Termux's own wiki — it's fire-and-
 * forget from the caller's side). So every step below that depends on Termux having
 * done something is verified by asking the script to write a small marker file into
 * shared storage, which THIS app can see directly, rather than trusting that firing
 * the intent means it worked.
 */
object TermuxBridge {

    private const val TERMUX_PKG = "com.termux"
    private const val TERMUX_BOOT_PKG = "com.termux.boot"
    private const val TERMUX_API_PKG = "com.termux.api"

    // Shared storage root our app can write to directly, and that Termux can also
    // see once termux-setup-storage has run (via its ~/storage/shared symlink).
    // Kept deliberately separate from /storage/emulated/0/maxhealth/ itself, so a
    // failed or half-finished provisioning attempt never touches the real app
    // folder — provision.sh only copies into the real location as its LAST step,
    // once everything else has succeeded.
    fun stagingDir(): File =
        File("/storage/emulated/0/maxhealth-launcher-staging")

    fun sentinelFile(name: String): File =
        File(stagingDir(), "sentinel_$name")

    fun isInstalled(context: Context, pkg: String): Boolean = try {
        context.packageManager.getPackageInfo(pkg, 0)
        true
    } catch (e: PackageManager.NameNotFoundException) {
        false
    }

    fun isTermuxInstalled(context: Context) = isInstalled(context, TERMUX_PKG)
    fun isTermuxBootInstalled(context: Context) = isInstalled(context, TERMUX_BOOT_PKG)
    fun isTermuxApiInstalled(context: Context) = isInstalled(context, TERMUX_API_PKG)

    /**
     * F-Droid, deliberately, not the Play Store — Termux and its plugin apps must
     * all be signed with the same key, and the versions distributed via F-Droid are
     * the ones that actually match each other. Mixing a Play Store Termux with
     * F-Droid Termux:Boot/API (or vice versa) is a known way to end up with
     * confusing permission failures that look unrelated to the real cause.
     */
    fun fdroidIntentFor(pkg: String): Intent =
        Intent(Intent.ACTION_VIEW, Uri.parse("https://f-droid.org/packages/$pkg/"))

    fun launchTermux(context: Context) {
        val intent = context.packageManager.getLaunchIntentForPackage(TERMUX_PKG)
        intent?.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent?.let { context.startActivity(it) }
    }

    /**
     * The one command that has to be pasted by hand, ever. Combines the two things
     * that both genuinely require a real Termux session to set (enabling
     * allow-external-apps, and running termux-setup-storage so Termux can see
     * shared storage) into a single paste rather than two separate manual steps.
     *
     * NEEDS VERIFYING ON DEVICE: whether termux-setup-storage pops its own Android
     * permission dialog here, or silently reuses the storage permission our own
     * app already requested earlier in the flow. Written defensively either way —
     * if it does pop a dialog, that's still just one more standard "Allow" tap
     * inside the same one-time step, not a new separate visit to Termux.
     */
    fun bootstrapCommand(): String =
        "echo \"allow-external-apps=true\" >> ~/.termux/termux.properties && " +
        "termux-reload-settings && " +
        "termux-setup-storage && " +
        "mkdir -p ~/storage/shared/maxhealth-launcher-staging && " +
        "touch ~/storage/shared/maxhealth-launcher-staging/sentinel_bootstrap"

    fun copyBootstrapCommandToClipboard(context: Context) {
        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboard.setPrimaryClip(ClipData.newPlainText("maxhealth-bootstrap", bootstrapCommand()))
    }

    /**
     * Writes provision.sh into the staging area (see stagingDir() above) so it's
     * ready the moment RUN_COMMAND becomes usable. This does NOT touch the real
     * /storage/emulated/0/maxhealth/ folder — provision.sh itself does that, as its
     * last step, only once everything before it has succeeded.
     */
    fun stageProvisionScript(context: Context, scriptContents: String) {
        stagingDir().mkdirs()
        File(stagingDir(), "provision.sh").writeText(scriptContents)
    }

    /**
     * Fires the actual RUN_COMMAND intent.
     *
     * RUN_COMMAND requires its target to be an executable file, but a file
     * staged on shared storage (/storage/emulated/0/...) can never be marked
     * executable — that's an Android filesystem limit, not a permission we
     * can grant our way around (confirmed on Pete's phone 23/09: chmod has no
     * effect there, error 405 "not executable" every time). So instead of
     * asking Termux to execute provision.sh directly, we ask it to run its
     * own bash — which IS executable, since it lives inside Termux's private
     * storage — and hand provision.sh to bash as something to read, exactly
     * like typing `bash provision.sh` at a prompt. bash only needs read
     * access to the script, which shared storage does allow.
     */
    fun runProvisionScript(context: Context) {
        val bashPath = "/data/data/com.termux/files/usr/bin/bash"
        val scriptPath =
            "/data/data/com.termux/files/home/storage/shared/maxhealth-launcher-staging/provision.sh"
        val intent = Intent().apply {
            setClassName(TERMUX_PKG, "com.termux.app.RunCommandService")
            action = "com.termux.RUN_COMMAND"
            putExtra("com.termux.RUN_COMMAND_PATH", bashPath)
            putExtra("com.termux.RUN_COMMAND_ARGUMENTS", arrayOf(scriptPath))
            putExtra("com.termux.RUN_COMMAND_BACKGROUND", true)
        }
        context.startForegroundService(intent)
    }

    /**
     * Actively nudges the server to (re)start, rather than only waiting and hoping
     * the watchdog's next once-a-minute tick catches it — this is what MainActivity's
     * Retry button (and every normal launch) calls before it starts polling /ping.
     *
     * Unlike provision.sh (staged on shared storage, so it has to be run via
     * `bash <path>` — see runProvisionScript's comment above), `mhstart` itself is
     * installed to `~/bin/mhstart` — that's inside Termux's own private storage
     * (confirmed on Pete's live phone, 22/09/26, and documented in TECHNICAL.md),
     * not shared storage, so it genuinely can be marked executable and RUN_COMMAND
     * can target it directly, no bash wrapper needed.
     */
    fun runMhstart(context: Context) {
        val mhstartPath = "/data/data/com.termux/files/home/bin/mhstart"
        val intent = Intent().apply {
            setClassName(TERMUX_PKG, "com.termux.app.RunCommandService")
            action = "com.termux.RUN_COMMAND"
            putExtra("com.termux.RUN_COMMAND_PATH", mhstartPath)
            putExtra("com.termux.RUN_COMMAND_BACKGROUND", true)
        }
        try {
            context.startForegroundService(intent)
        } catch (e: Exception) {
            // Best-effort nudge only — MainActivity still falls back to plain
            // polling/Retry if this doesn't fire for any reason, so a failure
            // here should never crash the launcher.
        }
    }

    /** True once the user has already granted this (Android remembers it permanently
     *  until manually revoked) — lets the caller skip showing the request screen
     *  again on every launch, which is what was happening before this check existed. */
    fun isIgnoringBatteryOptimizations(context: Context): Boolean {
        val pm = context.getSystemService(Context.POWER_SERVICE) as android.os.PowerManager
        return pm.isIgnoringBatteryOptimizations(context.packageName)
    }

    fun requestIgnoreBatteryOptimizations(context: Context) {
        val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
            data = Uri.parse("package:${context.packageName}")
        }
        // Optional step - some phones don't offer this screen, so never crash on it.
        try {
            context.startActivity(intent)
        } catch (e: android.content.ActivityNotFoundException) {
        }
    }
}
