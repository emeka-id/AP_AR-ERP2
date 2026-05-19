import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from uuid import uuid4

APP_TITLE = "PeopleSoft AP Voucher Processor"
DATA_FILE = "ap_data.json"

PROCESS_STEPS = [
    "Invoice received", "Voucher entered", "Matched", "Budget checked", "Approved",
    "Voucher posted", "Payment scheduled", "Payment created", "Payment posted",
]

INVOICE_FIELDS = [
    ("Invoice Number", "invoice_number"), ("Invoice Date", "invoice_date"), ("Accounting Date", "accounting_date"), ("Receipt Date", "receipt_date"),
    ("Invoice Type", "invoice_type"), ("Voucher ID", "voucher_id"), ("Voucher Style", "voucher_style"), ("Business Unit", "business_unit"),
    ("Supplier/Vendor ID", "vendor_id"), ("Supplier Name", "supplier_name"), ("Supplier Location", "supplier_location"), ("Vendor Tax ID", "vendor_tax_id"),
    ("Invoice Currency", "invoice_currency"), ("Exchange Rate Type", "exchange_rate_type"), ("Exchange Rate", "exchange_rate"), ("Gross Amount", "gross_amount"),
    ("Net Amount", "net_amount"), ("Tax Amount", "tax_amount"), ("Freight Amount", "freight_amount"), ("Miscellaneous Charges", "misc_charges"),
    ("Discount Amount", "discount_amount"), ("Payment Terms", "payment_terms"), ("Due Date", "due_date"), ("Payment Method", "payment_method"),
    ("Bank Account", "bank_account"), ("Payment Priority", "payment_priority"), ("Payment Group", "payment_group"), ("Invoice Description", "invoice_description"),
    ("Source", "source"), ("Entry Status", "entry_status"), ("Approval Status", "approval_status"), ("Match Status", "match_status"),
    ("Budget Status", "budget_status"), ("Posting Status", "posting_status"), ("Hold Status", "hold_status"), ("Hold Reason", "hold_reason"),
    ("Origin", "origin"), ("Created By", "created_by"), ("Created Timestamp", "created_ts"), ("Last Updated By", "updated_by"), ("Last Updated Timestamp", "updated_ts"),
]
PO_FIELDS = [("PO Number", "po_number"), ("PO Line Number", "po_line_number"), ("Receipt Number", "receipt_number"), ("Receiver ID", "receiver_id"), ("Buyer ID", "buyer_id"), ("PO Date", "po_date"), ("Contract ID", "contract_id"), ("Match Rule", "match_rule"), ("Match Exception Reason", "match_exception_reason"), ("Receiving Status", "receiving_status")]
LINE_FIELDS = [("Line Number", "line_number"), ("Item ID", "item_id"), ("Description", "line_description"), ("Quantity", "quantity"), ("Unit of Measure", "uom"), ("Unit Price", "unit_price"), ("Line Amount", "line_amount"), ("Tax Code", "tax_code"), ("Tax Amount", "line_tax_amount"), ("Freight Indicator", "freight_indicator"), ("Service Start Date", "service_start_date"), ("Service End Date", "service_end_date"), ("Asset Flag", "asset_flag"), ("Asset ID", "asset_id"), ("Project ID", "project_id"), ("Expense Category", "expense_category"), ("Cost Center", "cost_center")]
DIST_FIELDS = [("GL Business Unit", "gl_business_unit"), ("Account", "gl_account"), ("Department", "department"), ("Fund Code", "fund_code"), ("Program Code", "program_code"), ("Product Code", "product_code"), ("Project Code", "project_code"), ("Affiliate", "affiliate"), ("Operating Unit", "operating_unit"), ("ChartField Combination", "chartfield_combination"), ("Distribution Amount", "distribution_amount"), ("Distribution Percent", "distribution_percent"), ("Accrual Flag", "accrual_flag"), ("Budget Date", "budget_date")]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1500x940")
        self.fields = {}
        self.vendors, self.invoices, self.vouchers = [], [], []
        self.step_vars = {s: tk.BooleanVar(value=False) for s in PROCESS_STEPS}
        self._load_data()
        self._login()

    def _login(self):
        self.login_root = ttk.Frame(self, padding=20)
        self.login_root.pack(fill=tk.BOTH, expand=True)
        c = ttk.Frame(self.login_root, padding=20)
        c.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(c, text="PeopleSoft AP - Sign In", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(c, text="Username").grid(row=1, column=0, sticky="w")
        ttk.Label(c, text="Password").grid(row=2, column=0, sticky="w")
        ttk.Entry(c, width=32).grid(row=1, column=1, padx=4, pady=4)
        ttk.Entry(c, width=32, show="*").grid(row=2, column=1, padx=4, pady=4)
        ttk.Button(c, text="Sign In", command=self._post_login).grid(row=3, column=1, sticky="e")

    def _post_login(self):
        self.login_root.destroy()
        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        root = ttk.Frame(self, padding=6)
        root.pack(fill=tk.BOTH, expand=True)
        ttk.Button(root, text="New", command=self._open_invoice_info).pack(anchor="w", pady=2)
        self.nb = ttk.Notebook(root)
        self.nb.pack(fill=tk.BOTH, expand=True)
        self.nb.add(self._page_outstanding(), text="Outstanding Invoices")
        self.nb.add(self._page_vendors(), text="Vendors")
        self.nb.add(self._page_invoice_info(), text="Invoice Information Page")

    def _new_page(self):
        o = ttk.Frame(self.nb, padding=8)
        p = ttk.Frame(o, padding=8)
        p.pack(fill=tk.BOTH, expand=True)
        return o, p

    def _build_parallel_fields(self, parent, pairs):
        left, right = ttk.Frame(parent), ttk.Frame(parent)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        for i, (lbl, key) in enumerate(pairs):
            target = left if i % 2 == 0 else right
            r = i // 2
            ttk.Label(target, text=lbl).grid(row=r, column=0, sticky="w", padx=4, pady=2)
            v = tk.StringVar()
            ttk.Entry(target, textvariable=v, width=34).grid(row=r, column=1, sticky="w", padx=4, pady=2)
            self.fields[key] = v

    def _page_outstanding(self):
        o, p = self._new_page()
        ttk.Label(p, text="Outstanding Invoices", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        self.out_tree = ttk.Treeview(p, columns=("invoice", "vendor", "amount", "status"), show="headings", height=7)
        for c, t in [("invoice", "Invoice #"), ("vendor", "Vendor"), ("amount", "Amount"), ("status", "Status")]:
            self.out_tree.heading(c, text=t); self.out_tree.column(c, width=220)
        self.out_tree.pack(fill=tk.X)
        self.out_tree.bind("<<TreeviewSelect>>", self._on_invoice_select)
        self.inv_v_tree = ttk.Treeview(p, columns=("voucher", "invoice", "vendor", "status"), show="headings", height=6)
        for c, t in [("voucher", "Voucher ID"), ("invoice", "Invoice #"), ("vendor", "Vendor"), ("status", "Status")]:
            self.inv_v_tree.heading(c, text=t); self.inv_v_tree.column(c, width=220)
        self.inv_v_tree.pack(fill=tk.X, pady=8)
        self.v_tree = ttk.Treeview(p, columns=("voucher", "invoice", "vendor", "status", "gross"), show="headings", height=8)
        for c, t in [("voucher", "Voucher ID"), ("invoice", "Invoice #"), ("vendor", "Vendor"), ("status", "Status"), ("gross", "Gross")]:
            self.v_tree.heading(c, text=t); self.v_tree.column(c, width=170)
        self.v_tree.pack(fill=tk.BOTH, expand=True)
        return o

    def _page_vendors(self):
        o, p = self._new_page()
        frm = ttk.Frame(p); frm.pack(anchor="w")
        self._simple_entry(frm, "Vendor ID", "new_vendor_id", 0)
        self._simple_entry(frm, "Supplier Name", "new_vendor_name", 1)
        self._simple_entry(frm, "Supplier Location", "new_vendor_location", 2, "STANDARD")
        self._simple_entry(frm, "Vendor Tax ID", "new_vendor_tax_id", 3)
        ttk.Button(frm, text="Add Vendor", command=self._add_vendor).grid(row=4, column=1, sticky="w", pady=6)
        self.vendor_tree = ttk.Treeview(p, columns=("id", "name", "loc", "tax"), show="headings", height=12)
        for c, t in [("id", "Vendor ID"), ("name", "Supplier Name"), ("loc", "Location"), ("tax", "Tax ID")]:
            self.vendor_tree.heading(c, text=t); self.vendor_tree.column(c, width=260)
        self.vendor_tree.pack(fill=tk.BOTH, expand=True)
        self.vendor_tree.bind("<<TreeviewSelect>>", self._on_vendor_select)
        return o

    def _simple_entry(self, parent, label, key, row, default=""):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        v = tk.StringVar(value=default)
        ttk.Entry(parent, textvariable=v, width=34).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        self.fields[key] = v

    def _page_invoice_info(self):
        o, p = self._new_page()
        ttk.Label(p, text="Invoice Information Page", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        for title, fields in [
            ("Main Invoice Fields", INVOICE_FIELDS),
            ("PO / Matching Fields", PO_FIELDS),
            ("Invoice Line Fields", LINE_FIELDS),
            ("Distribution / ChartFields", DIST_FIELDS),
        ]:
            ttk.Label(p, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 4))
            frame = ttk.Frame(p); frame.pack(fill=tk.X)
            self._build_parallel_fields(frame, fields)
        ttk.Button(p, text="Save Invoice", command=self._save_invoice).pack(anchor="w", pady=10)
        return o

    def _open_invoice_info(self):
        self.nb.select(2)

    def _save_invoice(self):
        invoice_number = self.fields["invoice_number"].get().strip()
        vendor_id = self.fields["vendor_id"].get().strip()
        if not invoice_number or not vendor_id:
            messagebox.showerror("Invoice", "Invoice Number and Supplier/Vendor ID are required.")
            return
        if not any(v["vendor_id"] == vendor_id for v in self.vendors):
            messagebox.showerror("Invoice", "Vendor must exist first in Vendors tab.")
            return
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.fields["created_ts"].set(self.fields["created_ts"].get() or now)
        self.fields["updated_ts"].set(now)
        detail = {k: v.get().strip() for k, v in self.fields.items() if isinstance(v, tk.StringVar)}
        inv = {"invoice_id": str(uuid4())[:8], "invoice_number": invoice_number, "vendor_id": vendor_id, "gross_amount": detail.get("gross_amount", "0.00"), "status": detail.get("entry_status", "New"), "detail": detail}
        self.invoices.append(inv)
        voucher_id = detail.get("voucher_id") or str(100000 + len(self.vouchers) + 1)
        self.vouchers.append({"voucher_id": voucher_id, "invoice_number": invoice_number, "vendor_id": vendor_id, "gross_amount": detail.get("gross_amount", "0.00"), "status": detail.get("posting_status", "Entered")})
        self._save_data(); self._refresh_all()
        messagebox.showinfo("Saved", f"Invoice {invoice_number} saved; voucher {voucher_id} created.")

    def _add_vendor(self):
        vid = self.fields["new_vendor_id"].get().strip(); name = self.fields["new_vendor_name"].get().strip()
        loc = self.fields["new_vendor_location"].get().strip() or "STANDARD"; tax = self.fields["new_vendor_tax_id"].get().strip()
        if not vid or not name:
            messagebox.showerror("Vendor", "Vendor ID and Supplier Name are required."); return
        if any(v["vendor_id"] == vid for v in self.vendors):
            messagebox.showerror("Vendor", "Vendor ID already exists."); return
        self.vendors.append({"vendor_id": vid, "name": name, "location": loc, "tax_id": tax})
        self._save_data(); self._refresh_all()

    def _on_vendor_select(self, _):
        row = self.vendor_tree.focus()
        if not row: return
        vals = self.vendor_tree.item(row, "values")
        if "vendor_id" in self.fields:
            self.fields["vendor_id"].set(vals[0]); self.fields["supplier_name"].set(vals[1]); self.fields["supplier_location"].set(vals[2]); self.fields["vendor_tax_id"].set(vals[3])

    def _on_invoice_select(self, _):
        row = self.out_tree.focus()
        for i in self.inv_v_tree.get_children(): self.inv_v_tree.delete(i)
        if not row: return
        inv_no = self.out_tree.item(row, "values")[0]
        for v in [x for x in self.vouchers if x["invoice_number"] == inv_no]:
            self.inv_v_tree.insert("", tk.END, values=(v["voucher_id"], v["invoice_number"], v["vendor_id"], v["status"]))

    def _refresh_all(self):
        if hasattr(self, "vendor_tree"):
            for i in self.vendor_tree.get_children(): self.vendor_tree.delete(i)
            for v in self.vendors: self.vendor_tree.insert("", tk.END, values=(v["vendor_id"], v["name"], v["location"], v.get("tax_id", "")))
        if hasattr(self, "out_tree"):
            for i in self.out_tree.get_children(): self.out_tree.delete(i)
            for i in self.invoices: self.out_tree.insert("", tk.END, values=(i["invoice_number"], i["vendor_id"], i["gross_amount"], i["status"]))
        if hasattr(self, "v_tree"):
            for i in self.v_tree.get_children(): self.v_tree.delete(i)
            for v in self.vouchers: self.v_tree.insert("", tk.END, values=(v["voucher_id"], v["invoice_number"], v["vendor_id"], v["status"], v["gross_amount"]))

    def _save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"vendors": self.vendors, "invoices": self.invoices, "vouchers": self.vouchers}, f, indent=2)

    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            self.vendors = [{"vendor_id": "0000000044", "name": "Mel's Diner", "location": "STANDARD", "tax_id": ""}]
            return
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vendors = data.get("vendors", [])
        self.invoices = data.get("invoices", [])
        self.vouchers = data.get("vouchers", [])


if __name__ == "__main__":
    app = App()
    app.mainloop()
