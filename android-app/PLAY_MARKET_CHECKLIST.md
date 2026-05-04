# Play Market checklist

## Builddan oldin

- `android-app/keystore.properties.example` faylidan nusxa olib `keystore.properties` yarating
- Release keystore (`.jks`) yarating
- [app/build.gradle.kts](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/app/build.gradle.kts) ichida `versionCode` va `versionName` ni yangilang
- [strings.xml](/Users/asilbek/Desktop/AI-Projects/quiz-js/android-app/app/src/main/res/values/strings.xml:3) dagi `base_url` production domenga qarab turganini tekshiring
- Telefon va emulator’da login, test topshirish, admin panel, fayl yuklash va export funksiyalarini sinang

## Build

```bash
cd android-app
./gradlew bundleRelease
```

Natija:

```text
app/build/outputs/bundle/release/app-release.aab
```

## Play Console uchun tayyorlab qo'yish

- App nomi
- Qisqa tavsif
- To'liq tavsif
- 512x512 icon
- 1024x500 feature graphic
- Kamida 2 ta telefon screenshot
- Privacy Policy URL
- Support email
- App category: `Education`
- Content rating form
- Data safety form

## Tavsiya

Saytingizda alohida:

- `Privacy Policy` sahifa
- `Terms of Use` sahifa
- `Support` yoki `Contact` sahifa

bo'lsa, Play Console tasdiqlashidan o‘tish osonroq bo‘ladi.
