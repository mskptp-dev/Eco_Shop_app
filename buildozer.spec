[app]
title = Eco Shop Register
package.name = ecoshopregister
package.domain = org.tnforest.anamalai

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db

version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,fpdf2,sqlite3,pillow

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 27.3.13750724
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
