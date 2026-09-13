[app]
title = Eco Shop Register
package.name = ecoshopregister
package.domain = org.tnforest.anamalai

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db

version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,reportlab,sqlite3,pillow

# Orientation and behaviour
orientation = portrait
fullscreen = 0

# Icon / presplash - place your own files here (optional)
# icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

# Permissions needed: writing exported PDF/CSV registers to device storage
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
