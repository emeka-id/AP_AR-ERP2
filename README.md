# PeopleSoft AP Voucher Desktop App

This desktop app now supports:

- **Outstanding invoice list**
- **Per-invoice voucher visibility** (select invoice, see linked vouchers)
- **Global voucher status list**
- **Vendor management** (create new vendors + view vendor list)
- **Voucher creation tied to vendor + invoice**

## Run

```bash
python peoplesoft_ap_voucher_app.py
```

## Build Windows EXE

```bash
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name PeopleSoftAPVoucherApp peoplesoft_ap_voucher_app.py
```

Output:

- `dist/PeopleSoftAPVoucherApp.exe`

## Data files

- `ap_data.json`: persistent master data (vendors, invoices, vouchers)
- `voucher_session.json`: UI/session state
