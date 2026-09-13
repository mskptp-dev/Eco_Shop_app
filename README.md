# Eco Shop Register App — Anamalai Tiger Reserve

A Python (Kivy + KivyMD) Android app implementing the 5 registers you specified,
plus a Product Master with auto-generated unique product codes.

## What's included

| File/Folder | Purpose |
|---|---|
| `main.py` | App entry point, wires all screens together |
| `database.py` | SQLite backend — all tables, CRUD, monthly abstract, stock logic |
| `screens/dashboard.py` | Home screen with tiles for each register |
| `screens/products.py` | Product Master — add products, auto code (STK0001 / GRO0001...) |
| `screens/daily_sales.py` | Daily Sales Register |
| `screens/cash_register.py` | Cash Register (credit + debit) + Monthly Abstract |
| `screens/purchase_register.py` | Purchase Register (Grocery / Stock, linkable to Product Master) |
| `screens/stock_register.py` | Current Stock + Day-wise Stock (Year > Month > Date navigation) |
| `screens/bank_register.py` | Bank Transaction Register |
| `utils/pdf_export.py` | Exports any register to a printable PDF (and CSV) |
| `buildozer.spec` | Android packaging configuration |
| `.github/workflows/build.yml` | Builds the APK automatically in the cloud (see below) |

## How each register maps to your Excel sheet

- **Daily Sales Register** — S.No (auto), Date, Bill No. From/To, Total Amount Credited,
  Remarks (150 chars). You can save a zero-amount day too.
- **Cash Register** — separate Credit and Debit entry forms, combined table view,
  and a **Monthly Abstract** button that shows day-wise credit/debit + closing balance,
  exportable as PDF.
- **Purchase Register** — choose Grocery or Stock, enter vendor, bill no., item, quantity
  (Nos/Kg/Lt) and amount. If you link a purchase to a Stock product, current stock
  updates automatically.
- **Stock Register** — "Current Stock" tab shows live totals per product; "Day-wise Stock"
  tab opens on today by default and lets you step backward/forward by day or jump via
  the calendar (this is your Year > Month > Date navigation, done through the date picker).
- **Bank Transaction Register** — Date, Total Bills, Credited, Debited, with running
  balance calculated automatically from the previous entry.

Every register screen has an **Export** button that produces a formatted PDF table
(green header, Anamalai Tiger Reserve title) saved to the phone's Downloads folder,
ready to open or print with any PDF/print app installed on the device.

## Before you build: things to double check

1. **Dates** — the app uses KivyMD's built-in Material date picker (`MDModalDatePicker`),
   which behaves like a calendar app but runs inside the app itself. If you specifically
   want the phone's *native* Android calendar dialog to pop up (rather than this in-app
   one), that requires a small addition using `pyjnius` to call Android's
   `DatePickerDialog` directly — let me know and I'll add that variant.
2. **Printing** — the export currently saves a PDF file to `Download/EcoShopRegisters/`.
   Actually sending it straight to a printer (rather than opening the file first) needs
   Android's native print framework, again via `pyjnius`/`plyer`. Happy to wire that in
   once you've confirmed the basic flow works for you.
3. Rename `package.domain` in `buildozer.spec` if `org.tnforest.anamalai` isn't suitable.

## Building the APK

You need a Linux environment for Buildozer (it doesn't run on Windows). Three ways to get one:

### Option A — GitHub Actions (recommended, no Linux machine needed)
1. Create a new GitHub repository and push this folder to it.
2. GitHub will automatically run `.github/workflows/build.yml` on every push.
3. Go to the repo's **Actions** tab → open the latest run → download the
   `ecoshop-register-apk` artifact. That's your installable `.apk`.
4. Transfer it to your Android phone (via USB, email, or Drive) and install it
   (you'll need to allow "install from unknown sources" once).

### Option B — WSL2 (Windows Subsystem for Linux) on your own PC
```bash
sudo apt update && sudo apt install -y python3-pip build-essential git \
    libssl-dev libffi-dev python3-dev openjdk-17-jdk unzip
pip3 install --user buildozer cython
cd ecoshop_app
buildozer android debug
# APK will appear in ./bin/
```

### Option C — Test the UI on desktop first (fastest way to check the app logic)
Before packaging for Android, you can run it directly on a Linux/Mac machine (or WSL)
with a desktop Python install, to check the screens work:
```bash
pip install kivy kivymd reportlab
python main.py
```
(Date-picking, layout, and stock logic all work identically on desktop — only the
Android-specific storage path and permissions differ, which the code already
handles with a fallback.)

## Next steps you may want

- App icon and splash screen (drop `icon.png` / `presplash.png` in a `data/` folder
  and uncomment those two lines in `buildozer.spec`).
- A login/PIN screen if more than one shop staff will use the same phone.
- Backup/restore of the `ecoshop.db` file to Google Drive.
- Itemised sales (currently your Daily Sales Register only records bill-number ranges
  and a total, per your spec — if you'd later like per-item sales tied to the Product
  Master for a running "best sellers" report, that's a straightforward extension of
  `database.py`).

Let me know which of the above you'd like built out further, or if you'd like the
native-calendar / native-print variants instead of the in-app equivalents used here.
