# PeopleSoft AP Voucher Desktop App

## Changes
- Main UI **New** button now opens **Invoice Information Page**.
- Invoice Information Page supports **parallel fields** for all requested groups:
  - main invoice/header
  - PO/matching
  - invoice line
  - distribution/chartfields
- Saving invoice creates invoice + voucher records tied to vendor and shows them in outstanding/voucher lists.
- Launch sign-in still accepts any username/password.

## Run
```bash
python peoplesoft_ap_voucher_app.py
```

## Build EXE
```bash
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name PeopleSoftAPVoucherApp peoplesoft_ap_voucher_app.py
```
