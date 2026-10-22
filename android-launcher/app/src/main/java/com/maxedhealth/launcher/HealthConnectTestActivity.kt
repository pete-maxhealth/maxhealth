package com.maxedhealth.launcher

import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Switch
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.health.connect.client.HealthConnectClient
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

/**
 * TEMPORARY test screen (23/09/26) — its own launcher icon for today's
 * session only, so Pete can prove permission + read actually works on his
 * phone before this gets wired into the real onboarding flow and this
 * standalone icon gets removed. Deliberately plain, programmatic views, same
 * style as MainActivity's status screen — no XML layout needed for a
 * throwaway test screen.
 *
 * The on/off switch here (24/09/26) is the real one — when this screen goes
 * away, the switch and the checkAndSync() gate on HealthConnectBridge.isEnabled()
 * need to move into wherever Health Connect actually lives in the real Settings
 * screen, not get dropped along with the rest of this throwaway UI.
 */
class HealthConnectTestActivity : ComponentActivity() {

    private lateinit var status: TextView
    private lateinit var enableSwitch: Switch

    private val requestPermissions =
        registerForActivityResult(HealthConnectBridge.requestPermissionsContract()) { granted ->
            // v1.4.1 — the core seven are enough to sync; the optional extras
            // (distance, resting HR, total calories) just add more data if granted.
            if (granted.containsAll(HealthConnectBridge.corePermissions)) {
                syncNow()
            } else {
                status.text = "Permission not granted for everything asked. " +
                    "Granted: ${granted.size} of ${HealthConnectBridge.permissions.size}.\n\n" +
                    "Tap the button to try again, or check Health Connect's own app " +
                    "(Settings → Apps → Health Connect → App permissions → MaxedHealth)."
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        status = TextView(this).apply {
            text = "Checking Health Connect…"
            textSize = 16f
            setTextColor(Color.WHITE)
            setPadding(48, 48, 48, 48)
        }

        enableSwitch = Switch(this).apply {
            text = "Sync with Health Connect"
            setTextColor(Color.WHITE)
            isChecked = HealthConnectBridge.isEnabled(this@HealthConnectTestActivity)
            setOnCheckedChangeListener { _, isChecked ->
                HealthConnectBridge.setEnabled(this@HealthConnectTestActivity, isChecked)
                checkAndSync()
            }
        }

        val button = Button(this).apply {
            text = "Grant permission & sync now"
            setOnClickListener { checkAndSync() }
        }

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.BLACK)
            addView(enableSwitch)
            addView(status)
            addView(button)
        }
        setContentView(layout)

        checkAndSync()
    }

    private fun checkAndSync() {
        if (!HealthConnectBridge.isEnabled(this)) {
            status.text = "Health Connect sync is turned off. No data is read or requested " +
                "while this switch is off — turn it back on above to resume."
            return
        }
        status.text = "Checking Health Connect…"
        try {
            val availability = HealthConnectBridge.availability(this)
            status.text = "Checking Health Connect… (status code: $availability)"
            when (availability) {
                HealthConnectClient.SDK_UNAVAILABLE -> {
                    status.text = "This phone doesn't support Health Connect at all " +
                        "(too old / not supported)."
                }
                HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> {
                    status.text = "Health Connect needs installing or updating first."
                    try {
                        startActivity(
                            Intent(Intent.ACTION_VIEW).apply {
                                data = Uri.parse(
                                    "market://details?id=com.google.android.apps.healthdata"
                                )
                            }
                        )
                    } catch (e: Exception) {
                        // No Play Store available to handle it — message above still stands.
                    }
                }
                else -> {
                    status.text = "Health Connect available. Checking existing permissions…"
                    lifecycleScope.launch {
                        try {
                            val already = HealthConnectBridge.hasEveryPermission(
                                this@HealthConnectTestActivity
                            )
                            if (already) {
                                syncNow()
                            } else {
                                status.text = "Requesting permission — Health Connect's " +
                                    "own screen should open now…"
                                requestPermissions.launch(HealthConnectBridge.permissions)
                            }
                        } catch (e: Exception) {
                            status.text = "Error checking permissions:\n${e.javaClass.simpleName}: ${e.message}"
                        }
                    }
                }
            }
        } catch (e: Exception) {
            status.text = "Error checking availability:\n${e.javaClass.simpleName}: ${e.message}"
        }
    }

    private fun syncNow() {
        lifecycleScope.launch {
            status.text = "Reading today's data…"
            try {
                val summary = HealthConnectBridge.readToday(this@HealthConnectTestActivity)
                HealthConnectBridge.writeToInbox(this@HealthConnectTestActivity, summary)
                status.text = "Success —\n\n" +
                    "Steps: ${summary.steps}\n" +
                    "Avg heart rate: ${summary.avgHeartRate?.let { "%.0f bpm".format(it) } ?: "no data today"}\n" +
                    "Latest weight: ${summary.latestWeightKg?.let { "%.1f kg".format(it) } ?: "no data today"}\n" +
                    "Sleep: ${summary.sleepHours?.let { "%.1f h".format(it) } ?: "no data today"}\n\n" +
                    "Written to the pipeline inbox — run update_health.py to fold it into combined.csv"
            } catch (e: Exception) {
                status.text = "Error reading Health Connect: ${e.message}"
            }
        }
    }
}
