plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

import java.util.Properties

val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("keystore.properties")

if (keystorePropertiesFile.exists()) {
    keystorePropertiesFile.inputStream().use { keystoreProperties.load(it) }
}

android {
    namespace = "com.jahonschool.quizjs"
    compileSdk = 34

    setProperty("archivesBaseName", "JS-TEST")

    defaultConfig {
        applicationId = "com.jahonschool.quizjs"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    signingConfigs {
        if (keystorePropertiesFile.exists()) {
            create("release") {
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
            }
        }
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }

        release {
            isMinifyEnabled = false
            isShrinkResources = false
            if (keystorePropertiesFile.exists()) {
                signingConfig = signingConfigs.getByName("release")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("androidx.activity:activity-ktx:1.9.0")
}

tasks.register<Copy>("exportDebugApk") {
    from(layout.buildDirectory.dir("outputs/apk/debug"))
    include("*.apk")
    rename { "JS-TEST.apk" }
    into(layout.buildDirectory.dir("outputs/final/debug"))
}

tasks.register<Copy>("exportReleaseApk") {
    from(layout.buildDirectory.dir("outputs/apk/release"))
    include("*.apk")
    rename { "JS-TEST.apk" }
    into(layout.buildDirectory.dir("outputs/final/release"))
}

afterEvaluate {
    tasks.named("assembleDebug") {
        finalizedBy("exportDebugApk")
    }

    tasks.named("assembleRelease") {
        finalizedBy("exportReleaseApk")
    }
}
