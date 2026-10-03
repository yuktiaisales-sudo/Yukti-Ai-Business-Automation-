Yukti-AI Android Launcher Icon Update

1. Backup your current Flutter project.
2. Copy:
   android/app/src/main/res/drawable/yukti_ai_app_icon.png
   into your project at the same path.
3. Open:
   android/app/src/main/AndroidManifest.xml
4. In the <application> tag:
   - change android:label="crm_ai_app" to android:label="Yukti-AI"
   - change the existing android:icon value to @drawable/yukti_ai_app_icon
   Do NOT delete other application attributes.
5. Save.
6. Run:
   flutter clean
   flutter pub get
   flutter run
7. If Android still shows the old icon, uninstall the old app from the phone,
   then run flutter run again. Android can cache launcher icons.

For Play Store production, we should later generate proper adaptive launcher
icons (mipmap-anydpi-v26 plus foreground/background resources) rather than
using the simple drawable icon.
