package com.maxedhealth.launcher

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.ActiveCaloriesBurnedRecord
import androidx.health.connect.client.records.DistanceRecord
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.HeartRateVariabilityRmssdRecord
import androidx.health.connect.client.records.OxygenSaturationRecord
import androidx.health.connect.client.records.RestingHeartRateRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.TotalCaloriesBurnedRecord
import androidx.health.connect.client.records.WeightRecord
import androidx.health.connect.client.request.AggregateRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.io.File
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit
/**
 * MaxedHealth already has working ingestion for Amazfit/Zepp, RingConn, and
 * Garmin — this does NOT replace that. It's a NEW, separate source: Health
 * Connect is Android's own hub that many apps/wearables write into directly,
 * so this reads FROM Health Connect rather than from a phone-specific export
 * file. Whatever's in Health Connect on this phone (from any app that writes
 * to it) shows up here.
 *
 * Scope today (23/09/26, time-limited session): read-only, four data types,
 * proof that permission + read actually works end to end on Pete's phone.
 * NOT yet done: wiring this into provisioning/onboarding flow, writing into
 * combined.csv's actual schema (field_sources.json attribution etc.) — for
 * now it writes a plain staging CSV that a follow-up Python script can fold
 * into the real pipeline next session, same pattern as data/inbox for other
 * sources.
 */
object HealthConnectBridge {

    // Whether the person has actually agreed to Health Connect syncing, tracked
    // separately from whether the phone HAS granted the underlying Android
    // permission. Revoking access via Android's own Settings screen works fine
    // on its own, but it's not discoverable — most people would never think to
    // look there. Since transparency is a stated design principle for this app,
    // not just a functional nicety, this gives an explicit, visible on/off
    // switch inside the app itself, not just a fallback that technically exists
    // elsewhere. Defaults to on: this only ever fills a gap (health_connect sits
    // last in every precedence list in update_health.py and can never override a
    // real device's own reading), so there's no harm case to default-protect
    // against, only a preference one.
    private const val PREFS_NAME = "health_connect_prefs"
    private const val KEY_ENABLED = "sync_enabled"

    fun isEnabled(context: Context): Boolean =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getBoolean(KEY_ENABLED, true)

    fun setEnabled(context: Context, enabled: Boolean) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit().putBoolean(KEY_ENABLED, enabled).apply()
    }

    // Two different package names exist for the same thing, depending on Android
    // version — confirmed on Pete's phone (Android 15) 23/09/26, App info:
    //   com.google.android.healthconnect.controller — built into the OS (Android 14+)
    //   com.google.android.apps.healthdata          — separate Play Store app (Android <14)
    // Passing the wrong one to getSdkStatus() is what was causing this to loop
    // without ever reaching the real permission screen. Check both, prefer
    // whichever is actually installed.
    private const val HEALTH_CONNECT_PKG_MODERN = "com.google.android.healthconnect.controller"
    private const val HEALTH_CONNECT_PKG_LEGACY = "com.google.android.apps.healthdata"

    private fun providerPackage(context: Context): String {
        val pm = context.packageManager
        return try {
            pm.getPackageInfo(HEALTH_CONNECT_PKG_MODERN, 0)
            HEALTH_CONNECT_PKG_MODERN
        } catch (e: android.content.pm.PackageManager.NameNotFoundException) {
            HEALTH_CONNECT_PKG_LEGACY
        }
    }

    // 30/09/26 — added HRV, SpO2 and active calories, on Pete's request after
    // noticing those three permanently empty on the Today screen. All three are
    // genuinely new (not a bug in the original four): the 23/09/26 session that
    // built this scoped itself to exactly steps/heart-rate/weight/sleep, on
    // purpose, as a proof-of-concept — it was never a complete list of what
    // Health Connect can offer, just what got wired up first. Whether these
    // three actually populate depends on whether RingConn (or any other app on
    // this phone) writes to these specific Health Connect record types — that's
    // unverified until it's actually run on Pete's phone; the manual RingConn
    // export (ringconn.py) is confirmed to carry HRV and SpO2 today, but that
    // says nothing about whether RingConn's LIVE Health Connect writes include
    // them too.
    // 01/10/26 (v1.4) — split in two. `corePermissions` are the seven the sync
    // has always needed; hasAllPermissions() (the gate the background service
    // checks before every run) only requires THESE, so installing v1.4 over
    // v1.3 can never silently stop a working sync just because Health Connect
    // hasn't been asked about the new record types yet. `permissions` (core +
    // extras) is what the permission screen REQUESTS, and readToday() reads each
    // extra only if it was actually granted.
    val corePermissions = setOf(
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(WeightRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
        HealthPermission.getReadPermission(HeartRateVariabilityRmssdRecord::class),
        HealthPermission.getReadPermission(OxygenSaturationRecord::class),
        HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
    )
    private val PERM_DISTANCE = HealthPermission.getReadPermission(DistanceRecord::class)
    private val PERM_RESTING_HR = HealthPermission.getReadPermission(RestingHeartRateRecord::class)
    private val PERM_TOTAL_CAL = HealthPermission.getReadPermission(TotalCaloriesBurnedRecord::class)
    val permissions = corePermissions + setOf(PERM_DISTANCE, PERM_RESTING_HR, PERM_TOTAL_CAL)

    /** SDK_UNAVAILABLE / SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED / SDK_AVAILABLE. */
    fun availability(context: Context): Int =
        HealthConnectClient.getSdkStatus(context, providerPackage(context))

    /**
     * Deliberately lenient — matches the logic HealthConnectTestActivity has
     * actually been tested with (26/09/26): treat anything that ISN'T explicitly
     * "unavailable" or "needs a provider update" as usable, rather than requiring
     * an exact match to SDK_AVAILABLE. A stricter exact-match version of this was
     * tried first for MainActivity's settings gear and silently hid it even
     * though Health Connect itself works fine on this phone — this is the same
     * check already proven correct elsewhere, so both call sites now agree.
     */
    fun isAvailable(context: Context): Boolean {
        val status = availability(context)
        return status != HealthConnectClient.SDK_UNAVAILABLE &&
            status != HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED
    }

    fun client(context: Context): HealthConnectClient =
        HealthConnectClient.getOrCreate(context)

    /** Pass to registerForActivityResult(...) in the calling Activity — Health
     *  Connect shows its OWN permission screen (not the usual Android dialog). */
    fun requestPermissionsContract() = PermissionController.createRequestPermissionResultContract()

    suspend fun hasAllPermissions(context: Context): Boolean {
        val granted = client(context).permissionController.getGrantedPermissions()
        return granted.containsAll(corePermissions)
    }

    /** 01/10/26 (v1.4.1) — core PLUS the optional extras. The background sync
     *  gates on hasAllPermissions() (core only) so an upgrade can't stop it, but
     *  the "Grant permission & sync now" screen must use THIS one: with only the
     *  core check it believed everything was already granted and never opened
     *  Health Connect's permission screen, so the three new permissions were
     *  never offered (Pete: "Health connect never offered anything"). */
    suspend fun hasEveryPermission(context: Context): Boolean {
        val granted = client(context).permissionController.getGrantedPermissions()
        return granted.containsAll(permissions)
    }

    data class DailySummary(
        val date: LocalDate,
        val steps: Long,
        val avgHeartRate: Double?,
        val latestWeightKg: Double?,
        val sleepHours: Double?,
        // Only ever non-empty on a genuine overlap day (see resolveSleepHours) —
        // carried through so writeToInbox can log + queue it. Empty on every
        // ordinary day: no sessions, one session, or clearly-separate sessions.
        val unresolvedSleepOverlap: List<SleepSourceSession> = emptyList(),
        // 30/09/26 — new. Null on any day nothing wrote one of these record types
        // to Health Connect, same convention as avgHeartRate/latestWeightKg above
        // (no reading ≠ zero, so never default to 0.0 here — that would look like
        // a real measurement in combined.csv instead of "nothing recorded").
        val avgHrvMs: Double? = null,
        val avgSpo2Pct: Double? = null,
        val activeCalories: Double? = null,
        // 01/10/26 (v1.4) — everything below is optional/null-when-absent, same
        // convention as above: a key is only written to the export when there's a
        // real reading, never a placeholder zero.
        val distanceM: Double? = null,
        val restingHr: Double? = null,
        val hrMin: Double? = null,
        val hrMax: Double? = null,
        val hrvMin: Double? = null,
        val hrvMax: Double? = null,
        val spo2Min: Double? = null,
        val spo2Max: Double? = null,
        val caloriesPassive: Double? = null,
        val sleepDetail: SleepDetail? = null,
    )

    /** Sleep stage minutes + bed/wake times + efficiency for today's resolved night. */
    data class SleepDetail(
        val deepMin: Long, val lightMin: Long, val remMin: Long, val awakeMin: Long,
        val bedtime: String, val wakeTime: String, val efficiencyPct: Double?,
    )

    /** Reads today's data (local device timezone) from Health Connect. */
    suspend fun readToday(context: Context): DailySummary {
        val zone = ZoneId.systemDefault()
        val today = LocalDate.now(zone)
        val start = today.atStartOfDay(zone).toInstant()
        val end = Instant.now()
        val range = TimeRangeFilter.between(start, end)
        val hc = client(context)

        // Steps: ask Health Connect to aggregate rather than summing raw records.
        // Several apps (phone, Zepp, RingConn...) each write their own StepsRecords
        // for the same walking, so summing records double-counts. aggregate()
        // applies the user's app-priority order and de-duplicates overlaps.
        // Falls back to the old sum only if aggregate itself fails.
        val steps = try {
            hc.aggregate(AggregateRequest(setOf(StepsRecord.COUNT_TOTAL), range))[StepsRecord.COUNT_TOTAL] ?: 0L
        } catch (e: Exception) {
            hc.readRecords(ReadRecordsRequest(StepsRecord::class, range)).records.sumOf { it.count }
        }

        val heartRates = hc.readRecords(ReadRecordsRequest(HeartRateRecord::class, range))
            .records.flatMap { it.samples }.map { it.beatsPerMinute }
        val avgHr = if (heartRates.isEmpty()) null else heartRates.average()
        val hrMin = heartRates.minOrNull()?.toDouble()
        val hrMax = heartRates.maxOrNull()?.toDouble()

        val weights = hc.readRecords(ReadRecordsRequest(WeightRecord::class, range)).records
        val latestWeight = weights.maxByOrNull { it.time }?.weight?.inKilograms

        // 01/10/26 — sleep gets its own, WIDER query range than `range` above.
        // Pete: "Total sleep 13h32m" showing before 11am — impossible, and not
        // the resolveSleepHours overlap logic (that part's working correctly on
        // whatever it's given). The actual bug: `range` starts at today's
        // midnight, but Health Connect's TimeRangeFilter matches any session
        // that OVERLAPS the window at all — so last night's real sleep session
        // (started ~22:00 yesterday, ended ~06:00 today) gets pulled into
        // "today"'s query too, alongside anything else. resolveSleepHours then
        // correctly sees two genuinely non-overlapping periods and sums them —
        // it's just summing last night's sleep plus itself, in effect: counted
        // once for yesterday, counted again in full for today.
        //
        // Fixed by querying sleep over a separate, backward-extended window
        // (yesterday noon onward, comfortably before any realistic bedtime) so
        // a session starting before midnight is fully captured, then keeping
        // only sessions that actually ENDED today — i.e. attributing each
        // night to the day you woke up on, which is what "today's sleep" means
        // to a person checking Trends in the morning.
        val sleepRangeStart = today.minusDays(1).atTime(12, 0).atZone(zone).toInstant()
        val sleepRange = TimeRangeFilter.between(sleepRangeStart, end)
        val sleeps = hc.readRecords(ReadRecordsRequest(SleepSessionRecord::class, sleepRange)).records
            .filter { it.endTime.atZone(zone).toLocalDate() == today }
        // 01/10/26 (v11) — sessions now carry their real ASLEEP intervals (from
        // the record's stages), not just start→end. See resolveSleep() below for
        // why: a session's span includes awake time, and summing/comparing spans
        // across two devices recording the same night is what produced 13h32m.
        val sleepSessions = sleeps.map { toSleepSession(it) }
        val sleepResolution = resolveSleep(today, sleepSessions)
        val sleepHours = sleepResolution.hours
        val overlap = sleepResolution.conflicts

        // 30/09/26 — HRV and SpO2 are both instantaneous-reading record types (a
        // single moment, like a spot-check), not duration records like sleep/steps
        // — so "today's value" is an average of however many spot readings landed
        // in the day, same averaging approach already used for heart rate above.
        val hrvReadings = hc.readRecords(ReadRecordsRequest(HeartRateVariabilityRmssdRecord::class, range))
            .records.map { it.heartRateVariabilityMillis }
        val avgHrv = if (hrvReadings.isEmpty()) null else hrvReadings.average()
        val hrvMin = hrvReadings.minOrNull()
        val hrvMax = hrvReadings.maxOrNull()

        val spo2Readings = hc.readRecords(ReadRecordsRequest(OxygenSaturationRecord::class, range))
            .records.map { it.percentage.value }
        val avgSpo2 = if (spo2Readings.isEmpty()) null else spo2Readings.average()
        val spo2Min = spo2Readings.minOrNull()
        val spo2Max = spo2Readings.maxOrNull()

        // Active calories IS a duration record (like steps) — most apps write
        // several segments through the day rather than one, so sum them the same
        // way steps are summed above, not averaged.
        val activeCalories: Double? = try {
            hc.aggregate(AggregateRequest(setOf(ActiveCaloriesBurnedRecord.ACTIVE_CALORIES_TOTAL), range))[ActiveCaloriesBurnedRecord.ACTIVE_CALORIES_TOTAL]
                ?.inKilocalories
        } catch (e: Exception) {
            val r = hc.readRecords(ReadRecordsRequest(ActiveCaloriesBurnedRecord::class, range)).records
            if (r.isEmpty()) null else r.sumOf { it.energy.inKilocalories }
        }

        // 01/10/26 (v1.4) — the extras. Each is read only if its permission was
        // granted AND wrapped so one failing read can never take the whole sync
        // (steps, sleep, etc.) down with it.
        val granted = try { hc.permissionController.getGrantedPermissions() } catch (e: Exception) { emptySet() }

        val distanceM: Double? = if (PERM_DISTANCE !in granted) null else try {
            hc.aggregate(AggregateRequest(setOf(DistanceRecord.DISTANCE_TOTAL), range))[DistanceRecord.DISTANCE_TOTAL]?.inMeters
        } catch (e: Exception) {
            try {
                val recs = hc.readRecords(ReadRecordsRequest(DistanceRecord::class, range)).records
                if (recs.isEmpty()) null else recs.sumOf { it.distance.inMeters }
            } catch (e2: Exception) { null }
        }

        val restingHr: Double? = if (PERM_RESTING_HR !in granted) null else try {
            val recs = hc.readRecords(ReadRecordsRequest(RestingHeartRateRecord::class, range)).records
            if (recs.isEmpty()) null else recs.map { it.beatsPerMinute.toDouble() }.average()
        } catch (e: Exception) { null }

        // Total calories minus active = the "passive"/resting burn the pipeline's
        // calories_passive column holds. Needs both; otherwise leave it out.
        val totalCalories: Double? = if (PERM_TOTAL_CAL !in granted) null else try {
            hc.aggregate(AggregateRequest(setOf(TotalCaloriesBurnedRecord.ENERGY_TOTAL), range))[TotalCaloriesBurnedRecord.ENERGY_TOTAL]?.inKilocalories
        } catch (e: Exception) {
            try {
                val recs = hc.readRecords(ReadRecordsRequest(TotalCaloriesBurnedRecord::class, range)).records
                if (recs.isEmpty()) null else recs.sumOf { it.energy.inKilocalories }
            } catch (e2: Exception) { null }
        }
        val caloriesPassive = if (totalCalories != null && activeCalories != null)
            maxOf(0.0, totalCalories - activeCalories) else null

        // Sleep stages only when the night resolved to a single number (a queued
        // conflict has no agreed night to describe).
        val sleepDetail = if (sleepHours == null) null else try {
            buildSleepDetail(sleeps, zone)
        } catch (e: Exception) { null }

        return DailySummary(
            today, steps, avgHr, latestWeight, sleepHours, overlap,
            avgHrvMs = avgHrv, avgSpo2Pct = avgSpo2, activeCalories = activeCalories,
            distanceM = distanceM, restingHr = restingHr, hrMin = hrMin, hrMax = hrMax,
            hrvMin = hrvMin, hrvMax = hrvMax, spo2Min = spo2Min, spo2Max = spo2Max,
            caloriesPassive = caloriesPassive, sleepDetail = sleepDetail,
        )
    }

    /**
     * 01/10/26 (v1.4) — stage totals for the night resolveSleep() settled on.
     * Same rule as the duration: one source -> its records; several sources not
     * overlapping in time -> all records (separate periods); several overlapping
     * (same night, two devices) -> the preferred device's records ONLY, never
     * both, so deep+light+REM always agrees with the sleep_duration written
     * beside it. Stage minutes are the union of that stage's intervals.
     */
    internal fun buildSleepDetail(records: List<SleepSessionRecord>, zone: ZoneId): SleepDetail? {
        if (records.isEmpty()) return null
        val bySource = records.groupBy { sourceLabel(it.metadata.dataOrigin.packageName) }
        val chosen: List<SleepSessionRecord> = if (bySource.size == 1) records else {
            val spans = bySource.values.map { g -> g.minOf { it.startTime } to g.maxOf { it.endTime } }.sortedBy { it.first }
            var runningEnd = spans[0].second
            var overlap = false
            for (i in 1 until spans.size) {
                if (spans[i].first < runningEnd) overlap = true
                if (spans[i].second > runningEnd) runningEnd = spans[i].second
            }
            if (!overlap) records else {
                val preferred = SLEEP_SOURCE_PREFERENCE.firstNotNullOfOrNull { p -> bySource[p] }
                preferred ?: bySource.values.first()
            }
        }
        fun stageMins(types: Set<Int>) = unionMinutes(
            chosen.flatMap { r -> r.stages.filter { it.stage in types }.map { it.startTime to it.endTime } }
        )
        val deep = stageMins(setOf(SleepSessionRecord.STAGE_TYPE_DEEP))
        val light = stageMins(setOf(SleepSessionRecord.STAGE_TYPE_LIGHT))
        val rem = stageMins(setOf(SleepSessionRecord.STAGE_TYPE_REM))
        val awake = stageMins(setOf(SleepSessionRecord.STAGE_TYPE_AWAKE, SleepSessionRecord.STAGE_TYPE_AWAKE_IN_BED))
        if (deep + light + rem + awake == 0L) return null // device wrote no stage data
        val start = chosen.minOf { it.startTime }
        val end = chosen.maxOf { it.endTime }
        val fmt = DateTimeFormatter.ofPattern("HH:mm")
        val inBed = unionMinutes(chosen.map { it.startTime to it.endTime })
        val asleep = unionMinutes(chosen.flatMap { toSleepSession(it).asleep })
        val eff = if (inBed > 0) (asleep * 100.0 / inBed).coerceAtMost(100.0) else null
        return SleepDetail(deep, light, rem, awake, start.atZone(zone).format(fmt), end.atZone(zone).format(fmt), eff)
    }

    /** One sleep reading from one source app, e.g. Zepp or RingConn — both write
     *  their own independent SleepSessionRecord into Health Connect for the same
     *  night, since Health Connect is a shared hub, not a single deduplicated
     *  truth (found 30/09/26, see resolveSleepHours doc below). */
    data class SleepSourceSession(
        val source: String,
        val start: Instant,
        val end: Instant,
        // 01/10/26 (v11) — the intervals actually spent ASLEEP (stages that
        // aren't awake / out-of-bed). Defaults to the whole span for a record
        // with no stage data. A session's start→end span includes awake time,
        // so spans overstate sleep (Zepp 01:56-09:16 = 7h20 span, 5h17 asleep).
        val asleep: List<Pair<Instant, Instant>> = listOf(start to end),
        // Only set on the per-source aggregates handed to the conflict queue.
        val asleepMinutes: Long? = null,
    )

    /** What resolveSleep() decided: either a number of hours, or (hours == null)
     *  a genuine cross-source disagreement, with one aggregate per source. */
    data class SleepResolution(val hours: Double?, val conflicts: List<SleepSourceSession> = emptyList())

    private val ASLEEP_STAGES = setOf(
        SleepSessionRecord.STAGE_TYPE_SLEEPING,
        SleepSessionRecord.STAGE_TYPE_LIGHT,
        SleepSessionRecord.STAGE_TYPE_DEEP,
        SleepSessionRecord.STAGE_TYPE_REM,
    )

    private fun toSleepSession(r: SleepSessionRecord): SleepSourceSession {
        val asleep = r.stages.filter { it.stage in ASLEEP_STAGES }.map { it.startTime to it.endTime }
        return SleepSourceSession(
            sourceLabel(r.metadata.dataOrigin.packageName), r.startTime, r.endTime,
            // No stages at all (or none counted as sleep): fall back to the span.
            asleep = if (asleep.isEmpty()) listOf(r.startTime to r.endTime) else asleep,
        )
    }

    /** Best-effort human label for whichever app wrote a given record — falls back
     *  to the raw package name if it's not one of the two sources seen in practice
     *  so far, rather than hiding an unrecognised source. */
    private fun sourceLabel(packageName: String): String = when {
        packageName.contains("zepp", ignoreCase = true) || packageName.contains("huami", ignoreCase = true) -> "zepp"
        packageName.contains("ringconn", ignoreCase = true) -> "ringconn"
        else -> packageName
    }

    /**
     * 30/09/26 — replaces an earlier one-line `sleeps.sumOf { duration }`, which
     * simply added every session for the day together. That's correct only when
     * sessions are genuinely separate (e.g. a nap hours after waking) — when two
     * DIFFERENT devices (Zepp, RingConn) each report a session for the SAME
     * night, summing double-counts it: two real ~6-7h nights became one
     * impossible ~12-13h day.
     *
     * A silent union of overlapping intervals (earliest start → latest end) was
     * considered and rejected: two different devices' sensors don't measure the
     * same night identically — they disagree by minutes at the fall-asleep/
     * wake-up edges — so a union isn't "the true span," it's a bias toward
     * whichever device happened to read more generously at each edge. There's
     * no algorithmic way to know which (or neither) reading is more accurate.
     *
     * So this function only handles the unambiguous case — and the FAR more
     * common one, since most days/users have at most one sleep source at all:
     *   - No sessions: null (nothing to report).
     *   - One session: its own duration, as before.
     *   - Multiple sessions with real gaps between them (no overlap at all):
     *     sum them — each is a genuinely separate sleep period, correctly kept.
     * The one case it deliberately does NOT resolve here is a genuine overlap
     * BETWEEN DIFFERENT SOURCES — two sources disagreeing about the same
     * night. That's not a number this function can respectably produce; it's
     * queued instead (see logSleepOverlapDetected/queueSleepOverlapForResolution
     * below) for the person to resolve themselves next time they open the app,
     * the same way a new-vs-existing food item asks before silently guessing.
     * This keeps the ordinary day cheap and silent — no log line, no queued
     * file — and only ever writes anything when there's a genuine conflict
     * worth a human's attention.
     *
     * 30/09/26, found live on Pete's phone: RingConn alone can report 20+
     * overlapping SleepSessionRecords for one night — it re-syncs in short
     * fragments rather than one session per sleep — which the first version
     * of this function misread as 20+ sources disagreeing. That's one
     * device's own noisy bookkeeping, not a conflict between devices, so
     * before ever looking for a genuine cross-source overlap, sessions from
     * the SAME source are merged into a single contiguous block per source
     * first (safe to union here — these aren't independent measurements of
     * the same event, they're one device's own fragments of its own
     * reading). Only if two or more DIFFERENT sources still overlap after
     * that per-source merge is it treated as a real conflict.
     */
    internal fun resolveSleepHours(date: LocalDate, sessions: List<SleepSourceSession>): Double? =
        resolveSleep(date, sessions).hours

    /**
     * 01/10/26 (v11) — rewritten after Pete's real-device screenshots. Today's
     * Trends showed 13h32m before noon. The raw Health Connect sessions were:
     * RingConn 01:23-06:13, RingConn nap 08:03-09:11, Zepp 01:56-09:16 — spans
     * adding to 13h18m. But both devices' own apps said he was ASLEEP for
     * exactly 5h17m: a span includes awake time, and the card that asks the
     * person to resolve a conflict offered "add them" across ALL three raw
     * spans. So:
     *   1. Everything is measured in ASLEEP time (stage intervals), not spans.
     *   2. Each source's sessions are collapsed to ONE total per source (union
     *      of its asleep intervals — a nap and a main sleep from one device
     *      are one device's story, not two "sources").
     *   3. One source -> its total. Several sources that don't overlap in
     *      time at all -> sum (separate periods, as before).
     *   4. Several sources overlapping (same night, two devices) -> compare
     *      their TOTALS. Within SLEEP_AGREE_TOLERANCE_MIN of each other they
     *      agree; use the preferred device's figure, no prompt. Only a real
     *      disagreement is queued for the person, one line per source.
     * Still deliberately never unions two devices' edges or sums two devices
     * recording the same night.
     */
    private const val SLEEP_AGREE_TOLERANCE_MIN = 20L
    private val SLEEP_SOURCE_PREFERENCE = listOf("ringconn", "zepp")

    internal fun resolveSleep(date: LocalDate, sessions: List<SleepSourceSession>): SleepResolution {
        if (sessions.isEmpty()) return SleepResolution(null)

        val perSource = sessions.groupBy { it.source }.map { (source, group) ->
            SleepSourceSession(
                source, group.minOf { it.start }, group.maxOf { it.end },
                asleepMinutes = unionMinutes(group.flatMap { it.asleep }),
            )
        }
        fun minsOf(s: SleepSourceSession) = s.asleepMinutes ?: 0L

        if (perSource.size == 1) return SleepResolution(minsOf(perSource[0]) / 60.0)

        // Do the sources overlap in time at all (same night)? Running max end.
        val sorted = perSource.sortedBy { it.start }
        var runningEnd = sorted[0].end
        var overlap = false
        for (i in 1 until sorted.size) {
            if (sorted[i].start < runningEnd) overlap = true
            if (sorted[i].end > runningEnd) runningEnd = sorted[i].end
        }
        if (!overlap) return SleepResolution(perSource.sumOf { minsOf(it) } / 60.0)

        val mins = perSource.map { minsOf(it) }
        if (mins.max() - mins.min() <= SLEEP_AGREE_TOLERANCE_MIN) {
            val preferred = SLEEP_SOURCE_PREFERENCE
                .firstNotNullOfOrNull { p -> perSource.firstOrNull { it.source == p } }
                ?: perSource[0]
            return SleepResolution(minsOf(preferred) / 60.0)
        }
        return SleepResolution(null, perSource)
    }

    /** Length of the union of intervals, in whole minutes — overlapping or
     *  touching pieces (one device's own fragments) count once. */
    private fun unionMinutes(intervals: List<Pair<Instant, Instant>>): Long {
        if (intervals.isEmpty()) return 0L
        val sorted = intervals.sortedBy { it.first }
        var curStart = sorted[0].first
        var curEnd = sorted[0].second
        var total = 0L
        for (i in 1 until sorted.size) {
            val (s, e) = sorted[i]
            if (s <= curEnd) {
                if (e > curEnd) curEnd = e
            } else {
                total += java.time.Duration.between(curStart, curEnd).toMinutes()
                curStart = s
                curEnd = e
            }
        }
        total += java.time.Duration.between(curStart, curEnd).toMinutes()
        return total
    }

    /**
     * Writes one JSON entry to the REAL pipeline inbox — extractors/health_connect.py
     * (new, 24/09/26) reads exactly this file and folds it into combined.csv via the
     * same run(inbox) contract every other device extractor uses. This replaces an
     * earlier version that wrote to the launcher's own separate staging folder,
     * which nothing in the real pipeline ever looked at.
     *
     * Field names deliberately match SOURCE_FIELDS['health_connect'] in
     * update_health.py: steps, sleep_duration (MINUTES, not hours — matches every
     * other device's convention and the pipeline's own validation range), hr_avg
     * (average heart rate — NOT hrv, a different Health Connect record type this
     * app doesn't read), weight.
     *
     * Reads any existing file first and replaces just today's entry, so re-syncing
     * the same day is safe and other days already in the file survive. The pipeline
     * archives this file into inbox/old/ after a successful run, same as every
     * other device's export — the launcher just needs to write a fresh one next
     * time it wants new data picked up.
     */
    fun writeToInbox(context: Context, summary: DailySummary) {
        val inboxDir = File("/storage/emulated/0/maxhealth/app/data/inbox")
        inboxDir.mkdirs()
        val file = File(inboxDir, "health_connect_export.json")
        val dateStr = summary.date.format(DateTimeFormatter.ISO_LOCAL_DATE)

        val existing: org.json.JSONArray = if (file.exists()) {
            try {
                org.json.JSONArray(file.readText())
            } catch (e: org.json.JSONException) {
                org.json.JSONArray() // Corrupt/empty file — start fresh rather than crash.
            }
        } else {
            org.json.JSONArray()
        }

        // Drop any existing entry for today, then add the fresh one.
        val kept = org.json.JSONArray()
        for (i in 0 until existing.length()) {
            val obj = existing.optJSONObject(i) ?: continue
            if (obj.optString("date") != dateStr) kept.put(obj)
        }

        val entry = org.json.JSONObject()
        entry.put("date", dateStr)
        entry.put("steps", summary.steps)
        if (summary.avgHeartRate != null) entry.put("hr_avg", summary.avgHeartRate)
        if (summary.latestWeightKg != null) entry.put("weight", summary.latestWeightKg)
        if (summary.sleepHours != null) entry.put("sleep_duration", (summary.sleepHours * 60).toInt())
        // 30/09/26 — field names match update_health.py's combined.csv columns
        // exactly (hrv in ms, spo2 as a percent, calories_active in kcal) — same
        // "omit means no override" contract as every other field here: a day
        // with nothing recorded just leaves the key out rather than writing a
        // misleading 0/null that would look like a real zero reading.
        if (summary.avgHrvMs != null) entry.put("hrv", summary.avgHrvMs)
        if (summary.avgSpo2Pct != null) entry.put("spo2", summary.avgSpo2Pct)
        if (summary.activeCalories != null) entry.put("calories_active", summary.activeCalories)
        // 01/10/26 (v1.4) — field names match combined.csv columns exactly.
        if (summary.distanceM != null) entry.put("distance_m", summary.distanceM)
        if (summary.restingHr != null) entry.put("hr_resting", summary.restingHr)
        if (summary.hrMin != null) entry.put("hr_min", summary.hrMin)
        if (summary.hrMax != null) entry.put("hr_max", summary.hrMax)
        if (summary.hrvMin != null) entry.put("hrv_min", summary.hrvMin)
        if (summary.hrvMax != null) entry.put("hrv_max", summary.hrvMax)
        if (summary.spo2Min != null) entry.put("spo2_min", summary.spo2Min)
        if (summary.spo2Max != null) entry.put("spo2_max", summary.spo2Max)
        if (summary.caloriesPassive != null) entry.put("calories_passive", summary.caloriesPassive)
        summary.sleepDetail?.let { d ->
            entry.put("sleep_deep", d.deepMin)
            entry.put("sleep_light", d.lightMin)
            entry.put("sleep_rem", d.remMin)
            entry.put("sleep_wake", d.awakeMin)
            entry.put("bedtime", d.bedtime)
            entry.put("wake_time", d.wakeTime)
            if (d.efficiencyPct != null) entry.put("sleep_efficiency", d.efficiencyPct)
        }
        kept.put(entry)

        file.writeText(kept.toString(2))

        // Genuine overlap for this date — nothing above wrote a sleep_duration
        // for it (it was left out on purpose, see resolveSleepHours), so this
        // is the only record of what happened today. Every ordinary day
        // (including the "clearly separate sessions, summed fine" case) skips
        // this entirely: no log line, no queued file — the log only ever grows
        // on a day that actually needs a person's attention.
        if (summary.unresolvedSleepOverlap.isNotEmpty()) {
            logSleepOverlapDetected(summary.date, summary.unresolvedSleepOverlap)
            queueSleepOverlapForResolution(summary.date, summary.unresolvedSleepOverlap)
        }
    }

    // ── Sleep-overlap logging + queueing ─────────────────────────────────────
    //
    // 30/09/26 — this only ever fires for a genuine overlap (see
    // resolveSleepHours's doc comment for why that's the one case this code
    // won't silently resolve itself): two different sleep sources reporting
    // for the same night, disagreeing enough that summing or unioning them
    // would produce a number nobody can vouch for. In practice this only
    // touches users who have more than one sleep-recording source feeding
    // Health Connect at once (e.g. Pete: Zepp + RingConn) — most users and
    // most days never reach this code path at all.
    //
    // Two things happen here, both deliberately minimal:
    //   1. One structured log line into the SAME pipeline.log the Python side
    //      already writes to and Pete already reads — not a separate log file
    //      he'd have to know to check. If this fires when it shouldn't, or
    //      with implausible times, it's visible right alongside every other
    //      day's pipeline activity. If it never fires, the log stays exactly
    //      as quiet as before this feature existed.
    //   2. The raw (unresolved) sessions are queued to a small shared JSON
    //      file for maxhealth.html to pick up next time Pete opens the app,
    //      and present as a comparison card (see showSleepConflictComparison()
    //      in maxhealth.html) — same shape as showAddFoodComparison() for a
    //      duplicate library item: side-by-side values, an explicit
    //      per-instance choice, no default silently applied. There's no
    //      "saved rule" here on purpose — every genuine overlap gets its own
    //      fresh prompt, because different nights can legitimately deserve
    //      different resolutions (a dead battery giving a short reading one
    //      night doesn't mean the same source is wrong every night).

    private val LOG_FILE = File("/storage/emulated/0/maxhealth/app/logs/pipeline.log")
    private const val MAX_LOG_LINES = 500

    private fun logSleepOverlapDetected(date: LocalDate, sessions: List<SleepSourceSession>) {
        val detail = sessions.joinToString(", ") { s ->
            val start = s.start.atZone(ZoneId.systemDefault()).format(DateTimeFormatter.ofPattern("HH:mm"))
            val end = s.end.atZone(ZoneId.systemDefault()).format(DateTimeFormatter.ofPattern("HH:mm"))
            "${s.source}: $start-$end (${s.asleepMinutes ?: java.time.Duration.between(s.start, s.end).toMinutes()}m asleep)"
        }
        appendToPipelineLog("health_connect", "sleep", "WARN",
            "Overlapping sleep sessions for $date, needs resolution — $detail")
    }

    private fun appendToPipelineLog(device: String, operation: String, status: String, message: String) {
        try {
            LOG_FILE.parentFile?.mkdirs()
            val ts = java.time.LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
            val line = "$ts | ${device.padEnd(10)} | ${operation.padEnd(8)} | ${status.padEnd(6)} | $message"
            val existing = if (LOG_FILE.exists()) LOG_FILE.readLines() else emptyList()
            val combined = (existing + line).takeLast(MAX_LOG_LINES)
            LOG_FILE.writeText(combined.joinToString("\n") + "\n")
        } catch (e: Exception) {
            // Logging must never be why a sync fails — the export write above
            // already succeeded regardless of what happens here.
        }
    }

    /**
     * Small, separate queue file (NOT folded into health_connect_export.json,
     * which the Python pipeline already consumes and archives on every run —
     * mixing an unresolved-conflict list into that file risks it being silently
     * archived away before the web app ever reads it). One entry per pending
     * date; re-syncing the same still-unresolved day safely replaces its entry
     * rather than duplicating it. maxhealth.html removes an entry once its
     * comparison card choice is saved (via server.py's /resolve-sleep-conflict).
     */
    private fun queueSleepOverlapForResolution(date: LocalDate, sessions: List<SleepSourceSession>) {
        try {
            val queueFile = File("/storage/emulated/0/maxhealth/app/data/sleep_conflicts_pending.json")
            queueFile.parentFile?.mkdirs()
            val dateStr = date.format(DateTimeFormatter.ISO_LOCAL_DATE)

            val existing: org.json.JSONArray = if (queueFile.exists()) {
                try { org.json.JSONArray(queueFile.readText()) } catch (e: org.json.JSONException) { org.json.JSONArray() }
            } else org.json.JSONArray()

            val kept = org.json.JSONArray()
            for (i in 0 until existing.length()) {
                val obj = existing.optJSONObject(i) ?: continue
                if (obj.optString("date") != dateStr) kept.put(obj)
            }

            val entry = org.json.JSONObject()
            entry.put("date", dateStr)
            entry.put("detected_at", java.time.LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME))
            val sessionsArr = org.json.JSONArray()
            sessions.forEach { s ->
                val sObj = org.json.JSONObject()
                sObj.put("source", s.source)
                sObj.put("start", s.start.toString())
                sObj.put("end", s.end.toString())
                sObj.put("duration_minutes", s.asleepMinutes ?: java.time.Duration.between(s.start, s.end).toMinutes())
                sessionsArr.put(sObj)
            }
            entry.put("sessions", sessionsArr)
            kept.put(entry)

            queueFile.writeText(kept.toString(2))
        } catch (e: Exception) {
            // Same rationale as appendToPipelineLog — a queueing failure
            // shouldn't take down the rest of the sync.
        }
    }

    /** Registers the periodic background sync. Safe to call every app launch —
     *  KEEP policy means it's a no-op if already scheduled. 30 min matches the
     *  cadence of the update_health.py cron job that consumes what this writes. */
    fun schedulePeriodicSync(context: Context) {
        val request = PeriodicWorkRequestBuilder<HealthConnectSyncWorker>(30, TimeUnit.MINUTES).build()
        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            HealthConnectSyncWorker.WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            request
        )
    }
}
