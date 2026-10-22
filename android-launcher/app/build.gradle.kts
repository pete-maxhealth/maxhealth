plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.maxedhealth.launcher"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.maxedhealth.launcher"
        minSdk = 26
        targetSdk = 37
        // 01/10/26 — bumped for the first time tonight. versionCode had been
        // stuck at 1 through every build shipped so far (v3 through v8, all
        // real fixes: the SCHEDULE_EXACT_ALARM crash, HRV/SpO2/calories,
        // the settings-button timing fix) — harmless until now since nothing
        // compared it to anything, but the version-check below needs a real,
        // incrementing number to tell "installed" from "available" apart.
        // versionCode is what that comparison uses (a plain integer, bump by
        // 1 each release); versionName is just the human-readable label
        // shown in the app and in apk/version.json.
        // 01/10/26 — v10: fixes sleep double-counting (last night's session was
        // leaking into today's total via the HC query window, see
        // HealthConnectBridge.kt's readToday() for the full story).
        // 01/10/26 — v11: sleep is now resolved in ASLEEP time per source (see
        // HealthConnectBridge.resolveSleep) after v10's window fix turned out not to
        // be what caused 13h32m.
        // 01/10/26 — v12 / "1.4": reads more Health Connect metrics (distance, resting
        // HR, total calories, HR/SpO2/HRV min-max, sleep stages and bed/wake times).
        // v13 / "1.4.1": fixes the grant screen never offering the new v1.4 permissions.
        versionCode = 15
        versionName = "1.5.1"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    // 01/10/26 — AGP 8+ turns this off by default; MainActivity's update
    // check (checkForNewerApk) reads BuildConfig.VERSION_CODE to compare
    // against apk/version.json, which doesn't exist as a generated class at
    // all unless this is explicitly turned back on.
    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation(libs.androidx.activity.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.core.ktx)
    implementation(libs.material)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
    implementation("androidx.activity:activity-ktx:1.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.0")
    implementation("androidx.browser:browser:1.8.0")
    implementation("androidx.health.connect:connect-client:1.1.0")
    implementation("androidx.work:work-runtime-ktx:2.9.1")
}