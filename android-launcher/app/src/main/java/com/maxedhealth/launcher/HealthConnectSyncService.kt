package com.maxedhealth.launcher

import android.app.AlarmManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.SystemClock
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Replaces WorkManager for background Health Connect sync (29/09/26).
 *
 * WorkManager's own periodic job (HealthConnectSyncWorker, scheduled via
 * HealthConnectBridge.schedulePeriodicSync — kept in the codebase, not
 * deleted, in case a future MIUI/HyperOS update stops killing it) never
 * fired ONCE on Pete's phone in nearly an hour of testing — confirmed via
 * Android Studio's own Logcat (tag:WM-WorkerWrapper), which showed dozens of
 * OTHER apps' periodic workers firing normally in that same window, just
 * never ours. Battery saver for this app was already off, so this isn't the
 * usual "just turn off battery optimization" fix — something about HyperOS
 * (MIUI's newer name) is preventing WorkManager's periodic jobs from ever
 * being dispatched for this app specifically, before they even start (no
 * "worker started then killed" log line either — it never starts at all).
 *
 * A foreground service with a visible notification is the standard fallback
 * for exactly this situation: Android's process-management contract
 * explicitly protects a running foreground service (it must show the user a
 * notification while alive, which is the trade-off for that protection),
 * and manufacturer battery managers are far more reluctant to kill a
 * process the OS itself is actively supposed to keep running. This service:
 *   1. Starts itself in the foreground immediately (mandatory within a few
 *      seconds of startForegroundService() on Android 8+, or the system
 *      kills the app outright — ANR-style enforcement).
 *   2. Runs one sync immediately, then reschedules itself 30 minutes later
 *      via AlarmManager.setExactAndAllowWhileIdle() (Doze-resistant, unlike
 *      a plain AlarmManager.set()) rather than looping/sleeping inside the
 *      service itself, which would keep it (and its wake lock) alive
 *      continuously instead of only for the few seconds each sync actually
 *      needs.
 *   3. Stops itself (stopSelf()) after each sync completes — the
 *      foreground-service "on" state is what's protected, not the elapsed
 *      time, so there's no benefit to staying foregrounded between syncs,
 *      only extra battery cost and a permanently-visible notification.
 *
 * Started from MainActivity.onCreate() (same call site WorkManager's
 * scheduling used) and re-armed by AlarmReceiver after each alarm fires, so
 * the chain is self-sustaining without needing the app to be opened again —
 * PROVIDED Android hasn't force-stopped the app entirely (see AlarmReceiver
 * for the boot-restart half of that).
 */
class HealthConnectSyncService : Service() {

    private var job: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO)

    companion object {
        const val CHANNEL_ID = "health_connect_sync"
        const val NOTIFICATION_ID = 4201
        const val ALARM_REQUEST_CODE = 4202
        const val SYNC_INTERVAL_MS = 30 * 60 * 1000L // 30 min — matches update_health.py's cron cadence

        /** Safe to call repeatedly (every app launch, every alarm fire) — just
         *  (re)points the single alarm slot at "now + 30 min", never stacks. */
        fun scheduleNextRun(context: Context) {
            val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            val intent = Intent(context, AlarmReceiver::class.java)
            val pendingIntent = PendingIntent.getBroadcast(
                context,
                ALARM_REQUEST_CODE,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            val triggerAt = SystemClock.elapsedRealtime() + SYNC_INTERVAL_MS

            // 30/09/26 — found the hard way: SCHEDULE_EXACT_ALARM being declared in the
            // manifest does NOT mean it's granted. On Android 12+ it's a "special app
            // access" permission — auto-granted only on 12/13 for most apps, but on 14+
            // (Pete's Android 15, targetSdk 37) it requires the user to flip "Alarms &
            // reminders" on for this app in Settings themselves; nothing here was ever
            // prompting for that. Calling setExactAndAllowWhileIdle() without checking
            // first throws a SecurityException straight out of MainActivity.onCreate()
            // (via startNow() below) — crashing the whole app on launch, every time,
            // with no on-screen error (Android just kills the activity silently; the
            // exception only shows up in the system's own crash log). canScheduleExactAlarms()
            // is the required check (API 31+ only — doesn't exist before that, hence the
            // SDK_INT guard) and falling back to a plain inexact set() when it's false
            // means the app opens and syncs either way — just without Doze-exempt exact
            // timing until the user grants it. Never crash-or-nothing for a permission
            // that isn't even runtime-requestable from a prompt like a normal one.
            val canScheduleExact = Build.VERSION.SDK_INT < Build.VERSION_CODES.S ||
                alarmManager.canScheduleExactAlarms()

            if (canScheduleExact) {
                // setExactAndAllowWhileIdle, not plain set()/setExact() — the "AllowWhileIdle"
                // variant is the one exempted from Doze's alarm-batching, which is the whole
                // point given WorkManager's own periodic API was already being silently
                // dropped. Still rate-limited by Android to roughly once every ~9 min under
                // strict Doze, which our 30-min cadence is comfortably above.
                alarmManager.setExactAndAllowWhileIdle(
                    AlarmManager.ELAPSED_REALTIME_WAKEUP,
                    triggerAt,
                    pendingIntent
                )
            } else {
                // No exact-alarm access yet — degrade instead of crashing. A plain set()
                // still fires (Android may batch/delay it under Doze, unlike the exact
                // variant), so sync keeps working, just without the same Doze-resistant
                // timing guarantee until the permission is granted.
                alarmManager.set(
                    AlarmManager.ELAPSED_REALTIME_WAKEUP,
                    triggerAt,
                    pendingIntent
                )
            }
        }

        /** Whether this app currently holds the special "Alarms & reminders" access
         *  needed for setExactAndAllowWhileIdle(). Always true before API 31, where the
         *  permission doesn't exist as a user-facing toggle at all. Exposed so
         *  MainActivity can offer the user a one-tap route to Settings instead of the
         *  app silently running on degraded (inexact) timing forever. */
        fun hasExactAlarmPermission(context: Context): Boolean {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) return true
            val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            return alarmManager.canScheduleExactAlarms()
        }

        /** Starts the service now (an immediate sync) AND arms the next alarm —
         *  called once from MainActivity.onCreate(). Everything after this first
         *  call is self-sustaining via AlarmReceiver re-arming on each fire. */
        fun startNow(context: Context) {
            val intent = Intent(context, HealthConnectSyncService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
            scheduleNextRun(context)
        }
    }

    override fun onCreate() {
        super.onCreate()
        log("onCreate")
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        log("onStartCommand — calling startForeground()")
        try {
            // On Android 14+ (API 34), a manifest-declared foregroundServiceType MUST
            // also be passed to startForeground() itself, as a
            // ServiceInfo.FOREGROUND_SERVICE_TYPE_* flag, or the call throws
            // immediately. First attempt (29/09/26) used FOREGROUND_SERVICE_TYPE_HEALTH
            // — wrong choice: confirmed via this log file, Android's "health" FGS type
            // additionally requires ACTIVITY_RECOGNITION, BODY_SENSORS, or
            // HIGH_SAMPLING_RATE_SENSORS (a real SecurityException on Pete's Android 15
            // phone, targetSdk 37 — "health" is for apps reading LIVE sensor data, e.g.
            // a workout tracker, not for what this service actually does). Switched to
            // "dataSync" — the correct type for reading some data (here: from Health
            // Connect, itself already permission-gated separately) and writing it
            // somewhere (here: the pipeline inbox file), no extra sensor permissions
            // needed. Manifest's android:foregroundServiceType must match this exactly.
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                startForeground(
                    NOTIFICATION_ID,
                    buildNotification(),
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
                )
            } else {
                startForeground(NOTIFICATION_ID, buildNotification())
            }
            log("startForeground() succeeded")
        } catch (e: Exception) {
            log("startForeground() THREW: ${e.javaClass.simpleName}: ${e.message}")
            stopSelf()
            return START_NOT_STICKY
        }
        job = scope.launch {
            try {
                val enabled = HealthConnectBridge.isEnabled(applicationContext)
                val available = HealthConnectBridge.isAvailable(applicationContext)
                val permitted = HealthConnectBridge.hasAllPermissions(applicationContext)
                log("gating: enabled=$enabled available=$available permitted=$permitted")
                if (enabled && available && permitted) {
                    val summary = HealthConnectBridge.readToday(applicationContext)
                    HealthConnectBridge.writeToInbox(applicationContext, summary)
                    log("sync complete: steps=${summary.steps}")
                } else {
                    log("sync skipped — one or more gating checks failed")
                }
            } catch (e: Exception) {
                log("sync THREW: ${e.javaClass.simpleName}: ${e.message}")
                // Next scheduled run (30 min) will retry naturally — no separate
                // retry logic needed, unlike WorkManager's Result.retry(), since
                // AlarmManager's next fire is already coming regardless.
            } finally {
                stopSelf()
            }
        }
        return START_NOT_STICKY // We manage our own restart via the alarm, not the OS's sticky-restart.
    }

    /**
     * Plain-text trace file, NOT just Logcat (added 29/09/26) — Logcat access
     * turned out to be unreliable to read back for diagnosing this exact issue
     * (no keyboard access to Android Studio's filter box from Claude's side,
     * and saved filter shortcuts weren't catching this service's own tag).
     * Appends one line per event to a file next to the pipeline inbox, so it
     * can be inspected the same way as any other pipeline file — via Termux,
     * or staged/read directly — without needing Logcat at all. Deliberately
     * tiny and dependency-free (no logging library) since this only needs to
     * answer "did it even get this far" while tracking down this one bug;
     * fine to remove once background sync is confirmed reliable.
     */
    private fun log(message: String) {
        try {
            val dir = File("/storage/emulated/0/maxhealth/app/data")
            dir.mkdirs()
            val file = File(dir, "sync_service_debug.log")
            val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date())
            file.appendText("[$timestamp] $message\n")
        } catch (e: Exception) {
            // Best-effort diagnostic only — never let logging itself break the service.
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        log("onDestroy")
        job?.cancel()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Health Connect sync",
                NotificationManager.IMPORTANCE_MIN // Silent, no icon badge — this runs for a few
                // seconds every 30 min and has nothing the user needs to be interrupted for.
            ).apply {
                description = "Brief background sync with Health Connect"
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("MaxedHealth")
            .setContentText("Syncing Health Connect…")
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .setPriority(NotificationCompat.PRIORITY_MIN)
            .setOngoing(true)
            .build()
    }
}
