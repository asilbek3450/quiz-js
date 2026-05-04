# Android ilova

Ushbu papka saytingiz uchun Android ilovani o'z ichiga oladi. Ilova `WebView` asosida ishlaydi va mavjud saytingizni mobil ko'rinishda ochadi.

## Nimalar tayyor

- Kotlin asosidagi Android Studio loyiha
- `WebView` ichida saytni ochish
- Orqaga qaytish (`Back`) navigatsiyasi
- `Pull to refresh`
- Internet bo'lmasa xato sahifasi
- Saytdagi fayl yuklash inputlari uchun file chooser
- Yuklab olinadigan fayllar uchun `DownloadManager`
- Play Marketga mos package nomi va release tuzilmasi
- Release signing uchun tayyor Gradle ulanishi
- Android 12+ splash screen
- Play Market listing va privacy policy shablonlari

## Muhim sozlama

Sayt manzili [strings.xml](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/app/src/main/res/values/strings.xml:3) ichida turadi:

```xml
<string name="base_url">https://jahonschool.pythonanywhere.com</string>
```

Agar domen o'zgarsa, faqat shu qiymatni almashtirasiz.

## Ishga tushirish

1. Android Studio'da `android-app` papkasini oching.
2. Gradle sync qiling.
3. `./gradlew assembleDebug` yoki Android Studio orqali ishga tushiring.

## Play Market uchun keyingi qadamlar

1. [keystore.properties.example](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/keystore.properties.example) asosida `keystore.properties` yarating.
2. Release keystore yarating.
3. `versionCode` va `versionName` ni oshirib boring.
4. `./gradlew bundleRelease` orqali `.aab` yarating.
5. [PLAY_MARKET_CHECKLIST.md](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/PLAY_MARKET_CHECKLIST.md) bo'yicha Play Console'ga yuklang.

## Qo'shimcha fayllar

- [PLAY_MARKET_LISTING_UZ.md](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/PLAY_MARKET_LISTING_UZ.md)
- [PRIVACY_POLICY_TEMPLATE.md](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/PRIVACY_POLICY_TEMPLATE.md)
- [PLAY_MARKET_CHECKLIST.md](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/PLAY_MARKET_CHECKLIST.md)

## Eslatma

Lokal muhitda `Java` o'rnatilmagani sababli bu yerda build ishlatib tekshira olmadim. Lekin Gradle wrapper va Android loyiha strukturasi tayyor qo'shildi.
