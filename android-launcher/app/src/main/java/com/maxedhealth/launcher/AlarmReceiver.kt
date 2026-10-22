package com.maxedhealth.launcher

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build

/**
 * Fires every 30 min (armed by HealthConnectSyncService.scheduleNextRun) and
 * also on device boot (see the RECEIVE_BOOT_COMPLETED intent-filter in the
 * manifest) — boot handling matters because AlarmManager alarms are cleared
 * by a reboot, so without re-arming here, one restart of the phone would
 * silently end all future syncs until the app was manually reopened.
 *
 * Deliberately a plain BroadcastReceiver, not tied to any Activity being
 * open — this is exactly the background-without-a-visible-screen case the
 * whole foreground-service approach exists for.
 */
class AlarmReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Only re-arm on boot if sync was actually turned on before the
            // reboot — respects the same on/off switch HealthConnectTestActivity
            // exposes, rather than silently re-enabling something the user
            // may have deliberately turned off.
            if (!HealthConnectBridge.isEnabled(context)) return
        }
        val serviceIntent = Intent(context, HealthConnectSyncService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(serviceIntent)
        } else {
            context.startService(serviceIntent)
        }
        HealthConnectSyncService.scheduleNextRun(context)
    }
}
