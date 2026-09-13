from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.toast import toast
from datetime import date

import database as db

KV = """
<CashRegisterScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Cash Register"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 4
            md_bg_color: 0.18, 0.49, 0.20, 1

        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            padding: "8dp"
            spacing: "8dp"

            MDRaisedButton:
                text: "Add Credit"
                icon: "plus-circle-outline"
                on_release: root.open_credit_dialog()

            MDRaisedButton:
                text: "Add Debit"
                icon: "minus-circle-outline"
                md_bg_color: 0.72, 0.11, 0.11, 1
                on_release: root.open_debit_dialog()

            MDRaisedButton:
                text: "Monthly Abstract"
                icon: "calendar-month-outline"
                md_bg_color: 0.30, 0.30, 0.30, 1
                on_release: root.show_monthly_abstract()

        BoxLayout:
            id: table_holder
"""

Builder.load_string(KV)


class CashRegisterScreen(MDScreen):
    dialog = None
    picked_date = None

    def on_pre_enter(self, *args):
        self.refresh_table()

    def go_back(self):
        self.manager.current = "dashboard"

    @staticmethod
    def _display_date(iso):
        y, m, d = iso.split("-")
        return f"{d}/{m}/{y}"

    def refresh_table(self):
        holder = self.ids.table_holder
        holder.clear_widgets()
        credit, debit = db.get_cash_register()
        rows = []
        for c in credit:
            rows.append((self._display_date(c["date"]), "CREDIT", c["bill_from"] or "-",
                         c["bill_to"] or "-", f'{c["total_amount"]:.2f}'))
        for d_ in debit:
            rows.append((self._display_date(d_["date"]), "DEBIT", d_["voucher_no"] or "-",
                         (d_["description"] or "")[:30], f'{d_["total_amount"]:.2f}'))
        rows.sort(key=lambda r: r[0])
        table = MDDataTable(
            size_hint=(1, 1),
            check=False,
            column_data=[
                ("Date", dp(28)), ("Type", dp(20)), ("Ref/Voucher No.", dp(30)),
                ("Bill To / Description", dp(40)), ("Amount (Rs.)", dp(28)),
            ],
            row_data=rows,
        )
        holder.add_widget(table)

    def _date_button(self):
        self.picked_date = date.today()
        btn = MDFlatButton(text=f"Date: {self.picked_date.strftime('%d/%m/%Y')}",
                            on_release=self.open_calendar)
        return btn

    def open_calendar(self, instance):
        picker = MDModalDatePicker(sel_year=self.picked_date.year,
                                    sel_month=self.picked_date.month,
                                    sel_day=self.picked_date.day)
        picker.bind(on_ok=self._on_date_ok, on_cancel=lambda x: picker.dismiss())
        self._active_date_btn = instance
        picker.open()

    def _on_date_ok(self, instance):
        sel = instance.get_date()[0]
        self.picked_date = sel
        self._active_date_btn.text = f"Date: {sel.strftime('%d/%m/%Y')}"
        instance.dismiss()

    def open_credit_dialog(self):
        self.date_btn = self._date_button()
        self.bill_from_field = MDTextField(hint_text="Bill No. From")
        self.bill_to_field = MDTextField(hint_text="Bill No. To")
        self.total_field = MDTextField(hint_text="Total Amount (Rs.)", input_filter="float")

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(230))
        for w in (self.date_btn, self.bill_from_field, self.bill_to_field, self.total_field):
            content.add_widget(w)

        self.dialog = MDDialog(
            title="Cash Register — Credit Entry",
            type="custom", content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SAVE", on_release=self.save_credit),
            ],
        )
        self.dialog.open()

    def save_credit(self, *args):
        db.add_cash_credit(
            self.picked_date.isoformat(),
            self.bill_from_field.text.strip(),
            self.bill_to_field.text.strip(),
            float(self.total_field.text or 0),
        )
        toast("Credit entry saved")
        self.dialog.dismiss()
        self.refresh_table()

    def open_debit_dialog(self):
        self.date_btn = self._date_button()
        self.voucher_field = MDTextField(hint_text="Voucher No.")
        self.desc_field = MDTextField(hint_text="Description (max 150 chars)", max_text_length=150)
        self.total_field = MDTextField(hint_text="Total Amount (Rs.)", input_filter="float")

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(230))
        for w in (self.date_btn, self.voucher_field, self.desc_field, self.total_field):
            content.add_widget(w)

        self.dialog = MDDialog(
            title="Cash Register — Debit Entry",
            type="custom", content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SAVE", on_release=self.save_debit),
            ],
        )
        self.dialog.open()

    def save_debit(self, *args):
        db.add_cash_debit(
            self.picked_date.isoformat(),
            self.voucher_field.text.strip(),
            self.desc_field.text.strip(),
            float(self.total_field.text or 0),
        )
        toast("Debit entry saved")
        self.dialog.dismiss()
        self.refresh_table()

    def show_monthly_abstract(self):
        today = date.today()
        abstract = db.get_monthly_abstract(today.year, today.month)
        rows = [
            (self._display_date(d), f'{v["credit"]:.2f}', f'{v["debit"]:.2f}')
            for d, v in abstract["daily"].items()
        ]
        table = MDDataTable(
            size_hint=(0.9, 0.7),
            check=False,
            column_data=[("Date", dp(30)), ("Credit (Rs.)", dp(30)), ("Debit (Rs.)", dp(30))],
            row_data=rows,
        )
        summary = (
            f"Total Credit: Rs. {abstract['total_credit']:.2f}   |   "
            f"Total Debit: Rs. {abstract['total_debit']:.2f}   |   "
            f"Closing Balance: Rs. {abstract['closing_balance']:.2f}"
        )
        content = MDBoxLayout(orientation="vertical", spacing=dp(8))
        content.add_widget(table)
        from kivymd.uix.label import MDLabel
        content.add_widget(MDLabel(text=summary, size_hint_y=None, height=dp(30), halign="center"))

        self.dialog = MDDialog(
            title=f"Monthly Abstract — {today.strftime('%B %Y')}",
            type="custom", content_cls=content,
            buttons=[
                MDFlatButton(text="EXPORT PDF", on_release=lambda x: self._export_abstract(abstract, today)),
                MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss()),
            ],
        )
        self.dialog.open()

    def _export_abstract(self, abstract, month_date):
        from utils.pdf_export import export_to_pdf
        rows = [[self._display_date(d), f'{v["credit"]:.2f}', f'{v["debit"]:.2f}']
                for d, v in abstract["daily"].items()]
        rows.append(["TOTAL", f'{abstract["total_credit"]:.2f}', f'{abstract["total_debit"]:.2f}'])
        path = export_to_pdf(
            f"Cash Register Monthly Abstract {month_date.strftime('%b_%Y')}",
            ["Date", "Credit", "Debit"], rows,
            subtitle=f"Closing balance: Rs. {abstract['closing_balance']:.2f}",
        )
        toast(f"Saved to {path}")
