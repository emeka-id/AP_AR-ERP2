import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from uuid import uuid4

APP_TITLE = "PeopleSoft AP Voucher Processor"
SAVE_FILE = "voucher_session.json"
DATA_FILE = "ap_data.json"

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

VOUCHER_STATUS_LIST = [
    "Entered",
    "Matched",
    "Approved",
    "Budget Valid",
    "Posted",
    "Scheduled",
    "Paid",
    "Payment Posted",
]


class PeopleSoftStyle:
    HEADER_BLUE = "#6f99c6"
    NAV_BLUE = "#5d88b7"
    BG = "#f2f4f7"
    PANEL = "#ffffff"


class VoucherDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1400x920")
        self.configure(bg=PeopleSoftStyle.BG)

        self.fields = {}
        self.step_vars = {s: tk.BooleanVar(value=False) for s in PROCESS_STEPS}
        self.vendors = []
        self.invoices = []
        self.vouchers = []

        self._load_master_data()
        self._build_styles()
        self._build_layout()
        self._refresh_all_lists()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("PS.TFrame", background=PeopleSoftStyle.BG)
        style.configure("Panel.TFrame", background=PeopleSoftStyle.PANEL)
        style.configure("PSHeader.TLabel", background=PeopleSoftStyle.HEADER_BLUE, foreground="white", font=("Segoe UI", 10, "bold"))

    def _build_layout(self):
        root = ttk.Frame(self, style="PS.TFrame", padding=8)
        root.pack(fill=tk.BOTH, expand=True)

        self._build_top_nav(root)

        action_bar = ttk.Frame(root)
        action_bar.pack(fill=tk.X, pady=4)
        ttk.Button(action_bar, text="New", command=self.clear_form).pack(side=tk.LEFT)
        ttk.Button(action_bar, text="Save Session", command=self.save_session).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="Load Session", command=self.load_session).pack(side=tk.LEFT)
        ttk.Button(action_bar, text="Save Master Data", command=self._save_master_data).pack(side=tk.LEFT, padx=4)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.notebook.add(self._page_dashboard(), text="Outstanding Invoices")
        self.notebook.add(self._page_vendors(), text="Vendors")
        self.notebook.add(self._page_create_voucher(), text="Create Voucher")
        self.notebook.add(self._page_invoice_info(), text="Invoice Information")
        self.notebook.add(self._page_approval(), text="Voucher Approval")
        self.notebook.add(self._page_posting(), text="Voucher Posting")
        self.notebook.add(self._page_payment(), text="Payment Processing")
        self.notebook.add(self._page_workflow(), text="Process Tracker")

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
        ttk.Label(parent, text=f"  {text}", style="PSHeader.TLabel", anchor="w").pack(fill=tk.X, pady=(8, 6))

    def _add_entry(self, parent, label, key, r, c=0, default="", width=24):
        ttk.Label(parent, text=label).grid(row=r, column=c, sticky="w", padx=4, pady=3)
        var = tk.StringVar(value=default)
        ttk.Entry(parent, textvariable=var, width=width).grid(row=r, column=c + 1, sticky="w", padx=4, pady=3)
        self.fields[key] = var

    def _page_dashboard(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Outstanding Invoices", font=("Segoe UI", 20, "bold")).pack(anchor="w")

        self._section_header(page, "Outstanding Invoice List")
        self.outstanding_tree = ttk.Treeview(page, columns=("invoice", "vendor", "amount", "status"), show="headings", height=8)
        for c, t in [("invoice", "Invoice #"), ("vendor", "Vendor"), ("amount", "Amount"), ("status", "Status")]:
            self.outstanding_tree.heading(c, text=t)
            self.outstanding_tree.column(c, width=170)
        self.outstanding_tree.pack(fill=tk.X)
        self.outstanding_tree.bind("<<TreeviewSelect>>", self._on_invoice_select)

        btns = ttk.Frame(page)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Create Voucher for Selected Invoice", command=self._create_voucher_from_selected_invoice).pack(side=tk.LEFT)

        self._section_header(page, "Vouchers for Selected Invoice")
        self.invoice_voucher_tree = ttk.Treeview(page, columns=("voucher_id", "invoice", "vendor", "status"), show="headings", height=8)
        for c, t in [("voucher_id", "Voucher ID"), ("invoice", "Invoice #"), ("vendor", "Vendor"), ("status", "Voucher Status")]:
            self.invoice_voucher_tree.heading(c, text=t)
            self.invoice_voucher_tree.column(c, width=170)
        self.invoice_voucher_tree.pack(fill=tk.X)

        self._section_header(page, "All Vouchers and Statuses")
        self.voucher_status_tree = ttk.Treeview(page, columns=("voucher_id", "invoice", "vendor", "status", "gross"), show="headings", height=8)
        for c, t in [("voucher_id", "Voucher ID"), ("invoice", "Invoice #"), ("vendor", "Vendor"), ("status", "Status"), ("gross", "Gross Amount")]:
            self.voucher_status_tree.heading(c, text=t)
            self.voucher_status_tree.column(c, width=160)
        self.voucher_status_tree.pack(fill=tk.BOTH, expand=True)
        return outer

    def _page_vendors(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Vendor Management", font=("Segoe UI", 20, "bold")).pack(anchor="w")

        self._section_header(page, "Create New Vendor")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Vendor ID", "new_vendor_id", 0)
        self._add_entry(frm, "Short Name", "new_vendor_short", 1)
        self._add_entry(frm, "Vendor Name", "new_vendor_name", 2)
        self._add_entry(frm, "Location", "new_vendor_location", 3, default="STANDARD")
        ttk.Button(frm, text="Add Vendor", command=self._add_vendor).grid(row=4, column=1, sticky="w", pady=6)

        self._section_header(page, "Vendor List")
        self.vendor_tree = ttk.Treeview(page, columns=("vendor_id", "short", "name", "location"), show="headings", height=14)
        for c, t in [("vendor_id", "Vendor ID"), ("short", "Short Name"), ("name", "Vendor Name"), ("location", "Location")]:
            self.vendor_tree.heading(c, text=t)
            self.vendor_tree.column(c, width=220)
        self.vendor_tree.pack(fill=tk.BOTH, expand=True)
        self.vendor_tree.bind("<<TreeviewSelect>>", self._on_vendor_select)
        return outer

    def _page_create_voucher(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Creation of a Voucher", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self._section_header(page, "Add a New Value")

        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Business Unit", "business_unit", 0, default="US001")
        self._add_entry(frm, "Voucher ID", "voucher_id", 1, default="NEXT")
        self._add_entry(frm, "Voucher Style", "voucher_style", 2, default="Regular Voucher")

        ttk.Label(frm, text="Vendor (Existing)").grid(row=3, column=0, sticky="w", padx=4, pady=3)
        self.vendor_combo = ttk.Combobox(frm, state="readonly", width=22)
        self.vendor_combo.grid(row=3, column=1, sticky="w", padx=4, pady=3)

        self._add_entry(frm, "Vendor ID", "vendor_id", 4)
        self._add_entry(frm, "Vendor Location", "vendor_location", 5, default="STANDARD")
        self._add_entry(frm, "Invoice Number", "invoice_number", 6)
        self._add_entry(frm, "Invoice Date", "invoice_date", 7, default=str(date.today()))
        self._add_entry(frm, "Gross Invoice Amount", "gross_invoice_amount", 8, default="0.00")

        ttk.Button(frm, text="Create Invoice + Voucher", command=self._create_invoice_and_voucher).grid(row=9, column=1, sticky="w", pady=6)
        return outer

    def _page_invoice_info(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Invoice Information", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self._section_header(page, "Invoice and Distribution")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Control Group", "control_group", 0)
        self._add_entry(frm, "Pay Terms", "pay_terms", 1, default="30")
        self._add_entry(frm, "Currency", "currency", 2, default="USD")
        self._add_entry(frm, "Description", "line_desc", 3)
        self._add_entry(frm, "GL Unit", "gl_unit", 4)
        self._add_entry(frm, "Account", "account", 5)
        self._add_entry(frm, "Dept", "dept", 6)
        return outer

    def _page_approval(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Voucher Approval Workflow", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self._section_header(page, "Approval")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Voucher Approval", "voucher_approval", 0, default="Pre-Approved")
        ttk.Label(frm, text="Voucher Status").grid(row=1, column=0, sticky="w", padx=4, pady=3)
        self.status_combo = ttk.Combobox(frm, values=VOUCHER_STATUS_LIST, state="readonly", width=22)
        self.status_combo.set("Approved")
        self.status_combo.grid(row=1, column=1, sticky="w", padx=4, pady=3)
        ttk.Button(frm, text="Update Selected Voucher Status", command=self._update_selected_voucher_status).grid(row=2, column=1, sticky="w", pady=6)
        return outer

    def _page_posting(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Voucher Posting", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self._section_header(page, "Posting Request")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Run Control ID", "run_control_id", 0, default="ABCD")
        self._add_entry(frm, "Process Name", "process_name", 1, default="AP_PSTVCHR")
        return outer

    def _page_payment(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Payment Processing", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self._section_header(page, "Payment Selection Criteria")
        frm = ttk.Frame(page)
        frm.pack(anchor="w")
        self._add_entry(frm, "Pay Cycle", "pay_cycle", 0, default="TEST")
        self._add_entry(frm, "Payment Method", "payment_method", 1, default="ACH")
        self._add_entry(frm, "Bank Account", "bank_account", 2)
        return outer

    def _page_workflow(self):
        outer, page = self._new_page()
        ttk.Label(page, text="Process Tracker", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        for i, step in enumerate(PROCESS_STEPS, start=1):
            ttk.Checkbutton(page, text=f"{i}. {step}", variable=self.step_vars[step]).pack(anchor="w", pady=2)
        self.progress = ttk.Label(page, text="Progress: 0/9")
        self.progress.pack(anchor="w", pady=6)
        ttk.Button(page, text="Update Progress", command=self.refresh_progress).pack(anchor="w")
        return outer

    def _add_vendor(self):
        vendor_id = self.fields["new_vendor_id"].get().strip()
        short = self.fields["new_vendor_short"].get().strip()
        name = self.fields["new_vendor_name"].get().strip()
        loc = self.fields["new_vendor_location"].get().strip() or "STANDARD"
        if not vendor_id or not name:
            messagebox.showerror("Vendor", "Vendor ID and Vendor Name are required.")
            return
        if any(v["vendor_id"] == vendor_id for v in self.vendors):
            messagebox.showerror("Vendor", "Vendor ID already exists.")
            return
        self.vendors.append({"vendor_id": vendor_id, "short_name": short, "name": name, "location": loc})
        self._refresh_vendor_lists()
        self._save_master_data()

    def _on_vendor_select(self, _evt):
        row = self.vendor_tree.focus()
        if not row:
            return
        vals = self.vendor_tree.item(row, "values")
        if vals:
            self.fields["vendor_id"].set(vals[0])
            self.fields["vendor_location"].set(vals[3])

    def _create_invoice_and_voucher(self):
        vendor_id = self.fields["vendor_id"].get().strip()
        invoice_no = self.fields["invoice_number"].get().strip()
        gross = self.fields["gross_invoice_amount"].get().strip() or "0.00"
        if not vendor_id or not invoice_no:
            messagebox.showerror("Create", "Vendor ID and Invoice Number are required.")
            return
        if not any(v["vendor_id"] == vendor_id for v in self.vendors):
            messagebox.showerror("Create", "Vendor does not exist. Create/select vendor first.")
            return
        invoice = {
            "invoice_id": str(uuid4())[:8],
            "invoice_number": invoice_no,
            "vendor_id": vendor_id,
            "gross_amount": gross,
            "status": "Outstanding",
        }
        self.invoices.append(invoice)
        voucher_id = self.fields["voucher_id"].get().strip()
        if voucher_id == "NEXT" or not voucher_id:
            voucher_id = str(100000 + len(self.vouchers) + 1)
        voucher = {
            "voucher_id": voucher_id,
            "invoice_number": invoice_no,
            "vendor_id": vendor_id,
            "gross_amount": gross,
            "status": "Entered",
        }
        self.vouchers.append(voucher)
        self.step_vars["Voucher entered"].set(True)
        self.refresh_progress()
        self._refresh_all_lists()
        self._save_master_data()
        messagebox.showinfo("Created", f"Invoice {invoice_no} and Voucher {voucher_id} created.")

    def _create_voucher_from_selected_invoice(self):
        row = self.outstanding_tree.focus()
        if not row:
            messagebox.showwarning("Invoice", "Select an outstanding invoice first.")
            return
        invoice_no = self.outstanding_tree.item(row, "values")[0]
        inv = next((i for i in self.invoices if i["invoice_number"] == invoice_no), None)
        if not inv:
            return
        voucher_id = str(100000 + len(self.vouchers) + 1)
        self.vouchers.append({
            "voucher_id": voucher_id,
            "invoice_number": inv["invoice_number"],
            "vendor_id": inv["vendor_id"],
            "gross_amount": inv["gross_amount"],
            "status": "Entered",
        })
        self._refresh_all_lists()
        self._save_master_data()

    def _on_invoice_select(self, _evt):
        row = self.outstanding_tree.focus()
        for i in self.invoice_voucher_tree.get_children():
            self.invoice_voucher_tree.delete(i)
        if not row:
            return
        invoice_no = self.outstanding_tree.item(row, "values")[0]
        linked = [v for v in self.vouchers if v["invoice_number"] == invoice_no]
        for v in linked:
            self.invoice_voucher_tree.insert("", tk.END, values=(v["voucher_id"], v["invoice_number"], v["vendor_id"], v["status"]))

    def _update_selected_voucher_status(self):
        row = self.voucher_status_tree.focus()
        if not row:
            messagebox.showwarning("Voucher", "Select a voucher from Outstanding Invoices > All Vouchers and Statuses.")
            return
        voucher_id = self.voucher_status_tree.item(row, "values")[0]
        new_status = self.status_combo.get().strip() or "Entered"
        for v in self.vouchers:
            if v["voucher_id"] == voucher_id:
                v["status"] = new_status
                break
        self._refresh_all_lists()
        self._save_master_data()

    def _refresh_vendor_lists(self):
        for i in self.vendor_tree.get_children():
            self.vendor_tree.delete(i)
        for v in self.vendors:
            self.vendor_tree.insert("", tk.END, values=(v["vendor_id"], v["short_name"], v["name"], v["location"]))
        combo_vals = [f"{v['vendor_id']} - {v['name']}" for v in self.vendors]
        self.vendor_combo["values"] = combo_vals
        if combo_vals:
            self.vendor_combo.current(0)

    def _refresh_invoice_lists(self):
        for i in self.outstanding_tree.get_children():
            self.outstanding_tree.delete(i)
        for inv in self.invoices:
            self.outstanding_tree.insert("", tk.END, values=(inv["invoice_number"], inv["vendor_id"], inv["gross_amount"], inv["status"]))

    def _refresh_voucher_lists(self):
        for i in self.voucher_status_tree.get_children():
            self.voucher_status_tree.delete(i)
        for v in self.vouchers:
            self.voucher_status_tree.insert("", tk.END, values=(v["voucher_id"], v["invoice_number"], v["vendor_id"], v["status"], v["gross_amount"]))

    def _refresh_all_lists(self):
        if hasattr(self, "vendor_tree"):
            self._refresh_vendor_lists()
        if hasattr(self, "outstanding_tree"):
            self._refresh_invoice_lists()
        if hasattr(self, "voucher_status_tree"):
            self._refresh_voucher_lists()

    def refresh_progress(self):
        done = sum(v.get() for v in self.step_vars.values())
        self.progress.configure(text=f"Progress: {done}/{len(PROCESS_STEPS)}")

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

    def _save_master_data(self):
        data = {"vendors": self.vendors, "invoices": self.invoices, "vouchers": self.vouchers}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_master_data(self):
        if not os.path.exists(DATA_FILE):
            self.vendors = [{"vendor_id": "0000000044", "short_name": "MELS-001", "name": "Mel's Diner", "location": "STANDARD"}]
            self.invoices = []
            self.vouchers = []
            return
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vendors = data.get("vendors", [])
        self.invoices = data.get("invoices", [])
        self.vouchers = data.get("vouchers", [])


if __name__ == "__main__":
    app = VoucherDesktopApp()
    app.mainloop()
