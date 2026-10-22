package com.maxedhealth.launcher

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

/**
 * Background counterpart to HealthConnectTestActivity's manual "sync now"
 * button — same isEnabled/isAvailable/hasAllPermissions gating that screen
 * already does, just without a person present to press anything. Can't
 * request Health Connect permission from here (that needs a foreground
 * Activity, same as any Android runtime permission) — if it hasn't been
 * granted yet via the test/settings screen, this quietly does nothing until
 * it has been.
 */
class HealthConnectSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        if (!HealthConnectBridge.isEnabled(applicationContext)) return Result.success()
        if (!HealthConnectBridge.isAvailable(applicationContext)) return Result.success()

        return try {
            if (!HealthConnectBridge.hasAllPermissions(applicationContext)) {
                return Result.success()
            }
            val summary = HealthConnectBridge.readToday(applicationContext)
            HealthConnectBridge.writeToInbox(applicationContext, summary)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    companion object {
        const val WORK_NAME = "health_connect_periodic_sync"
    }
}