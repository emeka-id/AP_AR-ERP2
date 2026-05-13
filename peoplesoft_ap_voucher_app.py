import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

APP_TITLE = "PeopleSoft AP Voucher Processor"
SAVE_FILE = "voucher_session.json"

PROCESS_STEPS = [
    "Invoice received",
    "Voucher entered",
    "Matched",
    "Budget checked",
    "Approved",
    "Voucher posted",
    "Payment scheduled",
    "Payment created",
    "Payment posted",
]


class PeopleSoftStyle:
    HEADER_BLUE = "#6f99c6"
    NAV_BLUE = "#5d88b7"
    BG = "#f2f4f7"
    PANEL = "#ffffff"
    BORDER = "#b8c6d6"


class VoucherDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1360x900")
        self.configure(bg=PeopleSoftStyle.BG)

        self.fields = {}
        self.step_vars = {s: tk.BooleanVar(value=False) for s in PROCESS_STEPS}

        self._build_styles()
        self._build_layout()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("PS.TFrame", background=PeopleSoftStyle.BG)
        style.configure("Panel.TFrame", background=PeopleSoftStyle.PANEL)
        style.configure("PSHeader.TLabel", background=PeopleSoftStyle.HEADER_BLUE, foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Nav.TLabel", background=PeopleSoftStyle.NAV_BLUE, foreground="white", font=("Segoe UI", 9, "bold"))

    def _build_layout(self):
        root = ttk.Frame(self, style="PS.TFrame", padding=8)
        root.pack(fill=tk.BOTH, expand=True)

        self._build_top_nav(root)

        action_bar = ttk.Frame(root)
        action_bar.pack(fill=tk.X, pady=4)
        ttk.Button(action_bar, text="New", command=self.clear_form).pack(side=tk.LEFT)
        ttk.Button(action_bar, text="Save", command=self.save_session).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="Load", command=self.load_session).pack(side=tk.LEFT)
        ttk.Button(action_bar, text="Mark current step complete", command=self.mark_current_step).pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.pages = {}
        self.pages["create"] = self._page_create_voucher()
        self.pages["invoice"] = self._page_invoice_info()
        self.pages["approval"] = self._page_approval()
        self.pages["posting"] = self._page_posting()
        self.pages["payment"] = self._page_payment()
        self.pages["workflow"] = self._page_workflow()

        self.notebook.add(self.pages["create"], text="Creation of a Voucher")
        self.notebook.add(self.pages["invoice"], text="Invoice Information")
        self.notebook.add(self.pages["approval"], text="Voucher Approval Workflow")
        self.notebook.add(self.pages["posting"], text="Voucher Posting")
        self.notebook.add(self.pages["payment"], text="Payment Processing")
        self.notebook.add(self.pages["workflow"], text="Process Tracker")

    def _build_top_nav(self, parent):
        bar = tk.Frame(parent, bg=PeopleSoftStyle.NAV_BLUE, height=40)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text="ORACLE", bg=PeopleSoftStyle.NAV_BLUE, fg="white", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=14)
        tk.Label(
            bar,
            text="Favorites   >   Main Menu   >   Accounts Payable   >   Vouchers/Payments",
            bg=PeopleSoftStyle.NAV_BLUE,
            fg="white",
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=16)

    def _new_page(self):
        outer = ttk.Frame(self.notebook, style="PS.TFrame", padding=8)
        page = ttk.Frame(outer, style="Panel.TFrame", padding=10)
        page.pack(fill=tk.BOTH, expand=True)
        return outer, page

    def _section_header(self, parent, text):
        lbl = ttk.Label(parent, text=f"  {text}", style="PSHeader.TLabel", anchor="w")
        lbl.pack(fill=tk.X, pady=(8, 6))

    def _add_entry(self, parent, label, key, r, c=0, default="", width=24):
        ttk.Label(parent, text=label).grid(row=r, column=c, sticky="w", padx=4, pady=3)
        var = tk.StringVar(value=default)
        ttk.Entry(parent, textvariable=var, width=width).grid(row=r, column=c + 1, sticky="w", padx=4, pady=3)
        self.fields[key] = var

    def _page_create_voucher(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Creation of a Voucher", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(page, text="Navigation: Accounts Payable > Vouchers > Add/Update > Regular Entry", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 6))
        self._section_header(page, "Add a New Value")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")

        defaults = {
            "business_unit": "US001", "voucher_id": "NEXT", "voucher_style": "Regular Voucher", "short_vendor": "MELS-001",
            "vendor_id": "0000000044", "vendor_location": "STANDARD", "invoice_number": "Regular - T&G",
            "invoice_date": str(date.today()), "gross_invoice_amount": "8500.00", "freight_amount": "0.00", "sales_tax_amount": "0.00",
            "misc_charge_amount": "0.00", "estimated_lines": "1"
        }
        self._add_entry(frm, "Business Unit", "business_unit", 0, default=defaults["business_unit"])
        self._add_entry(frm, "Voucher ID", "voucher_id", 1, default=defaults["voucher_id"])
        self._add_entry(frm, "Voucher Style", "voucher_style", 2, default=defaults["voucher_style"])
        self._add_entry(frm, "Short Vendor Name", "short_vendor", 3, default=defaults["short_vendor"])
        self._add_entry(frm, "Vendor ID", "vendor_id", 4, default=defaults["vendor_id"])
        self._add_entry(frm, "Vendor Location", "vendor_location", 5, default=defaults["vendor_location"])
        self._add_entry(frm, "Invoice Number", "invoice_number", 6, default=defaults["invoice_number"])
        self._add_entry(frm, "Invoice Date", "invoice_date", 7, default=defaults["invoice_date"])
        self._add_entry(frm, "Gross Invoice Amount", "gross_invoice_amount", 8, default=defaults["gross_invoice_amount"])
        self._add_entry(frm, "Freight Amount", "freight_amount", 9, default=defaults["freight_amount"])
        self._add_entry(frm, "Sales Tax Amount", "sales_tax_amount", 10, default=defaults["sales_tax_amount"])
        self._add_entry(frm, "Misc Charge Amount", "misc_charge_amount", 11, default=defaults["misc_charge_amount"])
        self.fields["tax_exempt"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Tax Exempt Flag", variable=self.fields["tax_exempt"]).grid(row=12, column=1, sticky="w", pady=2)
        self._add_entry(frm, "Estimated No. of Invoice Lines", "estimated_lines", 13, default=defaults["estimated_lines"])
        return outer

    def _page_invoice_info(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Invoice Information Page", font=("Segoe UI", 24, "bold")).pack(anchor="w")

        self._section_header(page, "Invoice Information")
        top = ttk.Frame(page)
        top.pack(fill=tk.X)
        left = ttk.Frame(top)
        right = ttk.Frame(top)
        left.pack(side=tk.LEFT, padx=(0, 30), anchor="n")
        right.pack(side=tk.LEFT, anchor="n")

        self._add_entry(left, "Vendor ID", "inv_vendor_id", 0, default="0000000044")
        self._add_entry(left, "Location", "inv_location", 1, default="STANDARD")
        self._add_entry(left, "Control Group", "control_group", 2)
        self._add_entry(left, "Invoice Lines Total", "invoice_lines_total", 3, default="8500.00")
        self._add_entry(left, "Currency", "currency", 4, default="USD")

        self._add_entry(right, "Pay Terms", "pay_terms", 0, default="30")
        self._add_entry(right, "Basis Date Type", "basis_date_type", 1, default="Inv Date")
        self._add_entry(right, "PO Unit", "po_unit", 2)
        self._add_entry(right, "PO Number", "po_number", 3)
        self._add_entry(right, "Copy From", "copy_from", 4, default="None")

        self._section_header(page, "Invoice Lines")
        line = ttk.Frame(page)
        line.pack(fill=tk.X)
        for i, (lbl, key, default) in enumerate([
            ("Distribute By", "distribute_by", "Amount"), ("Ship To", "ship_to", "US001"), ("Item", "item", ""),
            ("UOM", "uom", ""), ("Quantity", "quantity", ""), ("Unit Price", "unit_price", ""),
            ("Line Amount", "line_amount", "8500.00"), ("Description", "line_desc", ""),
        ]):
            self._add_entry(line, lbl, key, i // 2, c=(i % 2) * 2, default=default)

        self._section_header(page, "Distribution Lines (GL ChartFields)")
        dist = ttk.Frame(page)
        dist.pack(fill=tk.X)
        for i, (lbl, key) in enumerate([
            ("GL Unit", "gl_unit"), ("Account", "account"), ("Open Item", "open_item"), ("Oper Unit", "oper_unit"),
            ("Fund", "fund"), ("Dept", "dept"), ("Program", "program"), ("Amount", "dist_amount")
        ]):
            self._add_entry(dist, lbl, key, i // 2, c=(i % 2) * 2)
        return outer

    def _page_approval(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Voucher Approval Workflow", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self._section_header(page, "Workflow Approval")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Voucher Approval", "voucher_approval", 0, default="Pre-Approved")
        self._add_entry(frm, "Business Process", "business_process", 1)
        self._add_entry(frm, "Rule Set", "rule_set", 2)
        self._add_entry(frm, "Route Denials To", "route_denials_to", 3)
        self._add_entry(frm, "Currency", "approval_currency", 4, default="USD")
        return outer

    def _page_posting(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Voucher Posting", font=("Segoe UI", 24, "bold")).pack(anchor="w")

        self._section_header(page, "Voucher Posting Request")
        top = ttk.Frame(page)
        top.pack(anchor="w")
        self._add_entry(top, "Run Control ID", "run_control_id", 0, default="ABCD")
        self._add_entry(top, "Request ID", "request_id", 1, default="POSTING")
        self._add_entry(top, "Description", "posting_description", 2, default="Posting a Voucher")
        self._add_entry(top, "Process Frequency", "process_frequency", 3, default="Always Process")
        self._add_entry(top, "Post Voucher Option", "post_voucher_option", 4, default="Post Voucher")

        self._section_header(page, "Process Scheduler Request")
        sched = ttk.Frame(page)
        sched.pack(anchor="w")
        self._add_entry(sched, "Server Name", "server_name", 0)
        self._add_entry(sched, "Run Date", "run_date", 1, default=str(date.today()))
        self._add_entry(sched, "Run Time", "run_time", 2)
        self._add_entry(sched, "Process Name", "process_name", 3, default="AP_PSTVCHR")
        return outer

    def _page_payment(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Payment Processing", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self._section_header(page, "Payment Selection Criteria")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Pay Cycle", "pay_cycle", 0, default="TEST")
        self._add_entry(frm, "Pay From Date", "pay_from_date", 1, default=str(date.today()))
        self._add_entry(frm, "Pay Through Date", "pay_through_date", 2)
        self._add_entry(frm, "Payment Date", "payment_date", 3)
        self._add_entry(frm, "Payment Method", "payment_method", 4, default="ACH")
        self._add_entry(frm, "Bank Account", "bank_account", 5)
        self.fields["hold_status_off"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Hold status is OFF", variable=self.fields["hold_status_off"]).grid(row=6, column=1, sticky="w")
        return outer

    def _page_workflow(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Process Tracker", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(page, text="Invoice received → Voucher entered → Matched → Budget checked → Approved → Voucher posted → Payment scheduled → Payment created → Payment posted").pack(anchor="w", pady=(0, 10))
        for i, step in enumerate(PROCESS_STEPS, start=1):
            ttk.Checkbutton(page, text=f"{i}. {step}", variable=self.step_vars[step]).pack(anchor="w", pady=2)
        self.progress = ttk.Label(page, text="Progress: 0/9")
        self.progress.pack(anchor="w", pady=6)
        ttk.Button(page, text="Update Progress", command=self.refresh_progress).pack(anchor="w")
        return outer

    def refresh_progress(self):
        done = sum(v.get() for v in self.step_vars.values())
        self.progress.configure(text=f"Progress: {done}/{len(PROCESS_STEPS)}")

    def mark_current_step(self):
        idx = self.notebook.index(self.notebook.select())
        map_page_to_step = {0: "Voucher entered", 1: "Matched", 2: "Approved", 3: "Voucher posted", 4: "Payment scheduled"}
        step = map_page_to_step.get(idx)
        if step:
            self.step_vars[step].set(True)
            self.refresh_progress()

    def clear_form(self):
        for var in self.fields.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set("")
        for v in self.step_vars.values():
            v.set(False)
        self.refresh_progress()

    def save_session(self):
        payload = {k: (bool(v.get()) if isinstance(v, tk.BooleanVar) else v.get()) for k, v in self.fields.items()}
        payload["steps"] = {k: v.get() for k, v in self.step_vars.items()}
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        messagebox.showinfo("Saved", f"Session saved to {SAVE_FILE}")

    def load_session(self):
        if not os.path.exists(SAVE_FILE):
            messagebox.showwarning("Load", f"{SAVE_FILE} not found.")
            return
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        for k, var in self.fields.items():
            if k in payload:
                var.set(payload[k])
        for k, var in self.step_vars.items():
            var.set(bool(payload.get("steps", {}).get(k, False)))
        self.refresh_progress()


if __name__ == "__main__":
    app = VoucherDesktopApp()
    app.mainloop()
