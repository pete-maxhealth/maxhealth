package com.maxedhealth.launcher

import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.browser.customtabs.CustomTabsIntent
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Opens MaxedHealth in Chrome (as a Custom Tab) rather than a built-in WebView.
 *
 * Why: a WebView is a stripped-down browser with its own separate storage, so
 * the app lost photo logging, voice input, barcode scanning, downloads,
 * notifications and confirm pop-ups, and couldn't see the data already in
 * Chrome. A Custom Tab runs inside the user's real Chrome, so every feature
 * works as it does today and the existing data at http://localhost:5757 is
 * the same data — PROVIDED that data actually lives in regular Chrome and
 * not in an installed PWA (see below).
 *
 * IMPORTANT (found 23/09 on Pete's phone): a real daily-use MaxedHealth
 * icon can turn out to be a Chrome-installed PWA/WebAPK
 * (org.chromium.webapk.<hash> — confirmed via Settings > Apps > App info >
 * APK name), NOT a plain Chrome tab. Android gives an installed WebAPK its
 * own separate storage, walled off from regular Chrome, even for the exact
 * same URL — so a Custom Tab into plain Chrome can open a genuinely empty,
 * unrelated copy of the same site. Confirmed on Pete's phone: Chrome's own
 * "localhost:5757" site storage showed 3.9MB, the WebAPK's App info storage
 * showed 282KB.
 *
 * Fix: findInstalledWebApk() below asks PackageManager who actually handles
 * this app's own URL and picks out whichever result is a WebAPK, rather than
 * one person's package name hardcoded — a hash Chrome generates per device,
 * so the previous hardcoded version only ever worked on the one phone it was
 * captured from. Falls back to opening a plain Chrome Custom Tab if no
 * WebAPK is found at all (e.g. this ever runs on a phone with no installed
 * PWA — a genuinely new user, say).
 *
 * Flow: wait for server.py to answer /ping (it may still be starting after a
 * reboot), open the tab, and close this screen when the user closes the tab.
 */
class MainActivity : ComponentActivity() {

    private val serverUrl = "http://localhost:5757"

    private var tabOpened = false
    private var starting = false
    private var launchJob: Job? = null
    private lateinit var status: TextView
    private lateinit var retryButton: Button
    private lateinit var root: FrameLayout

    // 01/10/26 — this app has no store to push updates through (it isn't on
    // Play), so unlike the PWA (which has its own service-worker update
    // banner) there was previously no way at all to know a newer build
    // existed — Pete has to be told directly each time, in chat. This checks
    // a tiny version.json committed alongside every APK release, the same
    // "check a small file, compare to what's installed" idea as the PWA's
    // own update check, just with no service worker to hang it on here.
    // Raw GitHub content, not the API — no auth needed, no rate-limit risk
    // for a single small file fetched once per app open.
    private val versionCheckUrl =
        "https://raw.githubusercontent.com/pete-maxhealth/maxhealth/main/apk/version.json"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        status = TextView(this).apply {
            text = "Starting MaxedHealth…"
            textSize = 18f
            gravity = Gravity.CENTER
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.BLACK)
        }
        retryButton = Button(this).apply {
            text = "Retry"
            visibility = View.GONE
            setOnClickListener {
                visibility = View.GONE
                status.text = "Starting MaxedHealth…"
                starting = false
                onResume()
            }
        }
        val centerLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.BLACK)
            addView(status)
            addView(retryButton)
        }
        // Settings entry point for Health Connect. Deliberately a plain tap target
        // here rather than the long-press home-screen shortcut (res/xml/shortcuts.xml)
        // — confirmed 26/09/26 that HyperOS's launcher doesn't invoke static app
        // shortcuts at all (no menu appears on long-press, on any app), so that
        // shortcut is unreachable on Pete's actual phone. Kept the shortcut too, for
        // launchers that do support it, but this button is now the reliable path:
        // it's part of our own Activity, so it isn't at the mercy of what a given
        // launcher chooses to support.
        //
        // Only shown when Health Connect itself is actually usable on this device
        // (HealthConnectBridge.isAvailable() — checks the real SDK status, not just
        // whether the package is installed) — no point cluttering the loading screen
        // with a settings icon that would just fail on a phone/OS version where
        // Health Connect isn't available at all.
        root = FrameLayout(this).apply {
            setBackgroundColor(Color.BLACK)
            addView(centerLayout, FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            ))
        }
        if (HealthConnectBridge.isAvailable(this)) {
            // 30/09/26 — replaced the timed, tap-before-it-vanishes gear icon with a
            // plain, permanent button. Two attempts at making the gear catchable
            // (bigger target, longer delay) both failed per Pete: "way too fast" —
            // the real problem was never the size or the timing, it was that this
            // was a brief window at all. A normal button that just sits there,
            // labelled in words rather than a small glyph, removes the race
            // entirely: there's nothing to catch, it's simply present for as long
            // as this screen is, on every open, no delay needed to make it visible
            // for the first time.
            val settingsButton = Button(this).apply {
                text = "Health Connect settings"
                setOnClickListener {
                    // Still cancel the pending auto-open of MaxedHealth itself —
                    // without this, that coroutine (still running in the
                    // background, since pausing this Activity doesn't cancel it)
                    // fires a few moments later regardless of what the user just
                    // navigated to, colliding with this screen. Confirmed
                    // 26/09/26: this is what was actually behind "Site cannot be
                    // reached" seen right after tapping the gear — two
                    // navigations racing, not a bad tap. Still needed now the
                    // button itself is always tappable rather than racing a timer.
                    launchJob?.cancel()
                    starting = false
                    startActivity(Intent(this@MainActivity, HealthConnectTestActivity::class.java))
                }
            }
            // Generous top margin, not just internal button padding — apps
            // targeting Android 15 draw edge-to-edge by default, so content can
            // render UNDER the status bar unless it's pushed clear of it.
            // Centered (not TOP|END) since this is now a labelled button people
            // need to read, not a small icon tucked in a corner.
            val density = resources.displayMetrics.density
            val clearMargin = (56 * density).toInt()
            val params = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT,
                Gravity.TOP or Gravity.CENTER_HORIZONTAL
            )
            params.topMargin = clearMargin
            root.addView(settingsButton, params)
        }
        setContentView(root)
        // 01/10/26 — fire-and-forget, after setContentView so it can never delay
        // or block the normal open flow (the whole point of this screen). Runs
        // on its own coroutine, entirely independent of the auto-open sequence
        // in onResume() below — a slow or failed network check here has zero
        // effect on getting to MaxedHealth itself.
        lifecycleScope.launch { checkForNewerApk() }
        // Switched from WorkManager (HealthConnectBridge.schedulePeriodicSync) to a
        // foreground service + AlarmManager (29/09/26) — the WorkManager periodic job
        // never fired once on Pete's phone in nearly an hour of testing, confirmed via
        // Logcat showing other apps' workers firing normally in the same window. See
        // HealthConnectSyncService's own doc comment for the full story. The old
        // schedulePeriodicSync() call is kept in HealthConnectBridge.kt, unused, rather
        // than deleted — if a future HyperOS update fixes WorkManager scheduling this
        // can be revisited, but the foreground service is the reliable path for now.
        //
        // 30/09/26 — wrapped in try/catch: this call used to throw a SecurityException
        // straight out of onCreate() (missing SCHEDULE_EXACT_ALARM grant — see
        // HealthConnectSyncService.scheduleNextRun's doc comment, which is the actual
        // fix), which crashed the ENTIRE activity before setContentView's Custom Tab
        // could ever open — meaning a background-sync problem was taking down the
        // primary "open MaxedHealth" screen too. That root cause is now handled inside
        // scheduleNextRun() itself (falls back to an inexact alarm instead of crashing),
        // but this try/catch stays as a second line of defence: whatever happens with
        // background sync, it must never be able to stop this screen from opening.
        try {
            HealthConnectSyncService.startNow(this)
        } catch (e: Exception) {
            // Background sync failing to start is not something the person opening the
            // app to log food or check their data needs to see or be blocked by.
        }
        // 02/10/26 — ask once for "Alarms & reminders". Without it the 30-min sync alarm is
        // inexact and Android won't start the sync service from the background, so syncing
        // only happened while the app was open.
        try {
            if (!HealthConnectSyncService.hasExactAlarmPermission(this)) {
                val prefs = getSharedPreferences("launcher", MODE_PRIVATE)
                if (!prefs.getBoolean("exact_alarm_prompted", false)) {
                    prefs.edit().putBoolean("exact_alarm_prompted", true).apply()
                    startActivity(Intent(android.provider.Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,
                        Uri.parse("package:" + packageName)))
                }
            }
        } catch (e: Exception) { }
        tabOpened = savedInstanceState?.getBoolean("tabOpened") ?: false
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putBoolean("tabOpened", tabOpened)
    }

    override fun onResume() {
        super.onResume()
        if (tabOpened) {
            // Back here means the user closed the app's tab - close the launcher too.
            finish()
            return
        }
        if (starting) return
        starting = true
        TermuxBridge.runMhstart(this) // actively ensure the server, not just wait and hope
        val launchedAt = System.currentTimeMillis()
        launchJob = lifecycleScope.launch {
            // 30/09/26 — shown briefly on EVERY open, not just first-run onboarding.
            // Pete's reasoning: this app's home-screen icon looks, at a glance,
            // identical in purpose to the actual MaxedHealth PWA icon sitting next to
            // it — so months from now, either he or Jill could reasonably tap it,
            // see it just open the same MaxedHealth they already have another icon
            // for, and conclude this one's a redundant duplicate worth deleting. It
            // isn't — deleting this app silently kills the Health Connect background
            // sync along with it (see HealthConnectSyncService's doc comment: the
            // sync IS this app, not a separate thing it happens to also run). A
            // short explanation every time is the guard against that — cheap for a
            // rare tap, and exactly the moment someone's wondering "wait, what's
            // this one for" is when it's most useful to answer that, not just once
            // during setup and never again.
            status.text = "MaxedHealth Sync\n\n" +
                "This app runs the background connection to Health Connect — the " +
                "part that reads your sleep, steps and heart rate every 30 minutes " +
                "and feeds them into MaxedHealth. It's not a duplicate of the main " +
                "MaxedHealth icon; deleting this one stops that syncing.\n\n" +
                "Opening MaxedHealth…"
            // 01/10/26 — Pete still lost the race even with the permanent button
            // and a 2.2s pre-delay: "reloaded and it was back to a split second".
            // The button being permanent was never the real fix — this whole
            // screen still auto-finished itself the moment the server answered,
            // taking the button down with it. On a warm server (the ordinary
            // case, and the one that matters here) the old floor was really only
            // ~900ms end-to-end once you account for how these two waits stack,
            // not remotely enough to read the screen and react. Raised well
            // past anything that could still read as "a flash" — 6s is a real
            // pause on a warm launch, not nothing, but it only costs time on
            // every ordinary open, and the alternative (Pete unable to reach a
            // settings screen at all without outside help) is worse than a
            // slightly slower open.
            delay(2200)
            if (waitForServer()) {
                val elapsed = System.currentTimeMillis() - launchedAt
                val minDisplayMs = 6000L
                if (elapsed < minDisplayMs) delay(minDisplayMs - elapsed)

                // /ping answering only proves the server PROCESS is up — not that the
                // real page (the ~1.7MB HTML file at "/") is actually ready to serve.
                // Added 26/09/26: right after a fresh mhstart, there was a gap where
                // /ping (a trivial, always-fast route) answered a beat before the
                // real root route was ready to hand over the full page, producing a
                // brief "page not found" flash in Chrome/the WebAPK before the real
                // content loaded. This confirms the actual page, not just the
                // process, before handing off. Short retry rather than a hard
                // failure: if it's still not confirmed after ~2.5s, open anyway
                // rather than stacking a second retry screen on top of the first.
                var rootReady = rootPageReady()
                var rootAttempts = 0
                while (!rootReady && rootAttempts < 5) {
                    delay(500)
                    rootReady = rootPageReady()
                    rootAttempts++
                }
                openTargetApp()
            } else {
                // Confirmed on Pete's phone 25/09/26: the watchdog checks once a
                // minute and genuinely does catch and restart a dead server (real
                // log entries proved it) — but this used to give up after only 30s
                // and open a Chrome tab regardless, landing on a raw "can't be
                // reached" page seconds before the watchdog would have fixed it on
                // its own. Now it waits long enough to cover that worst case
                // (up to ~60s for the next tick, plus real startup time) and, if
                // it's STILL not up after that, shows an actual retry screen
                // instead of a doomed tab — retrying re-runs the same active
                // mhstart nudge, not just another passive wait.
                status.text = "MaxedHealth's server is taking longer than usual to start.\n\n" +
                    "It should recover on its own within about a minute — tap Retry to check again."
                retryButton.visibility = View.VISIBLE
                starting = false
            }
        }
    }

    /** Up to ~100 seconds — comfortably covers the watchdog's worst case (up to
     *  ~60s until its next once-a-minute check, plus real server.py startup
     *  time), not just an arbitrary short wait. Returns whether the server
     *  actually answered, so the caller can show a real retry option instead of
     *  opening a dead page when it didn't. */
    private suspend fun waitForServer(): Boolean {
        for (attempt in 1..100) {
            if (serverAnswers()) return true
            if (attempt == 3) status.text = "Waiting for MaxedHealth's server to start…"
            delay(1000)
        }
        return false
    }

    private suspend fun serverAnswers(): Boolean = withContext(Dispatchers.IO) {
        try {
            val conn = URL("$serverUrl/ping").openConnection() as HttpURLConnection
            conn.connectTimeout = 1000
            conn.readTimeout = 1000
            val ok = conn.responseCode == 200
            conn.disconnect()
            ok
        } catch (e: Exception) {
            false
        }
    }

    /** Confirms the real root page — not just /ping — is actually ready to serve.
     *  HEAD rather than GET so this doesn't pull the full ~1.7MB file just to
     *  check readiness. See the comment in onResume() for why this exists. */
    private suspend fun rootPageReady(): Boolean = withContext(Dispatchers.IO) {
        try {
            val conn = URL(serverUrl).openConnection() as HttpURLConnection
            conn.connectTimeout = 2000
            conn.readTimeout = 2000
            conn.requestMethod = "HEAD"
            val ok = conn.responseCode == 200
            conn.disconnect()
            ok
        } catch (e: Exception) {
            false
        }
    }

    /** Try Pete's real installed WebAPK first (has his actual data); fall back to a plain Chrome tab. */
    /**
     * Finds WHICHEVER installed WebAPK actually serves this app's own URL,
     * instead of one person's package name hardcoded (25/09/26 — the previous
     * version only worked on Pete's own phone; Jill or any other tester would
     * silently land on a genuinely empty Chrome tab, exactly like Pete's own
     * WebAPK/Chrome storage-split night). Works the same way Android itself
     * resolves "which app opens this link": ask PackageManager who handles an
     * explicit VIEW intent for this exact URL, and take whichever result is a
     * WebAPK (package name always starts org.chromium.webapk.) rather than
     * Chrome itself or anything else that happens to claim http links.
     */
    private fun findInstalledWebApk(): String? {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(serverUrl)).apply {
            addCategory(Intent.CATEGORY_BROWSABLE)
        }
        return try {
            packageManager.queryIntentActivities(intent, 0)
                .map { it.activityInfo.packageName }
                .firstOrNull { it.startsWith("org.chromium.webapk.") }
        } catch (e: Exception) {
            null
        }
    }

    private fun openTargetApp() {
        val webApkPackage = findInstalledWebApk()
        val webApkIntent = webApkPackage?.let { packageManager.getLaunchIntentForPackage(it) }
        if (webApkIntent != null) {
            try {
                startActivity(webApkIntent)
                tabOpened = true
                return
            } catch (e: ActivityNotFoundException) {
                // Fall through to Chrome below.
            }
        }
        openInChrome()
    }

    private fun openInChrome() {
        val tab = CustomTabsIntent.Builder()
            .setUrlBarHidingEnabled(true)
            .build()
        // Chrome specifically: another browser would have its own separate storage.
        tab.intent.setPackage("com.android.chrome")
        try {
            tab.launchUrl(this, Uri.parse(serverUrl))
            tabOpened = true
        } catch (e: ActivityNotFoundException) {
            status.text = "MaxedHealth needs Google Chrome. Install or enable Chrome, then open this app again."
            starting = false
        }
    }

    // 01/10/26 — this app's own equivalent of the PWA's "🔄 new version ready"
    // banner. Best-effort in every sense: a timeout, a bad/missing JSON, no
    // network, an unreachable GitHub — any of these just means the check
    // silently does nothing, same as "you're already current" from the
    // person's point of view. Nothing here is allowed to show an error or a
    // retry option; the alternative (a failed background check nagging
    // someone trying to log food) is worse than occasionally missing an
    // update notice.
    private suspend fun checkForNewerApk() {
        val newer = withContext(Dispatchers.IO) {
            try {
                val conn = URL(versionCheckUrl).openConnection() as HttpURLConnection
                conn.connectTimeout = 3000
                conn.readTimeout = 3000
                if (conn.responseCode != 200) return@withContext null
                val body = conn.inputStream.bufferedReader().readText()
                conn.disconnect()
                val json = JSONObject(body)
                val latestCode = json.optInt("versionCode", -1)
                val latestName = json.optString("versionName", "")
                if (latestCode <= BuildConfig.VERSION_CODE) return@withContext null
                latestName
            } catch (e: Exception) {
                null
            }
        } ?: return
        showApkUpdateBanner(newer)
    }

    // Separate from the "MaxedHealth Sync" explanation text — that one is
    // about what this app IS (shown every open, in the status TextView
    // itself); this is about a genuinely new build being available, which
    // is occasional, so it's a dismissible banner layered on top rather than
    // competing with the explanation for the same space.
    private fun showApkUpdateBanner(versionName: String) {
        if (isFinishing || isDestroyed) return
        val banner = TextView(this).apply {
            text = "🔄 MaxedHealth Sync v$versionName is available — tap for the download"
            textSize = 13f
            setTextColor(Color.parseColor("#080a0d"))
            setBackgroundColor(Color.parseColor("#2debaf"))
            setPadding(24, 16, 24, 16)
            setOnClickListener {
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(
                        "https://github.com/pete-maxhealth/maxhealth/tree/main/apk"
                    )))
                } catch (e: ActivityNotFoundException) {
                    // No browser available to open the link - nothing more to do here,
                    // the banner itself already said where to look.
                }
            }
        }
        val params = FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.WRAP_CONTENT,
            Gravity.BOTTOM
        )
        root.addView(banner, params)
    }
}
