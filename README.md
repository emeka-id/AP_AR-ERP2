# PeopleSoft AP Voucher Desktop App

This desktop app now mirrors the PeopleSoft-style page flow shown in your mockups:

- Creation of a Voucher
- Invoice Information (with invoice lines + distribution lines)
- Voucher Approval Workflow
- Voucher Posting
- Payment Processing
- End-to-end workflow tracker

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
