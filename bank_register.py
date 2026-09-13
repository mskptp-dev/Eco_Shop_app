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
<BankRegisterScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Bank Transaction Register"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 4
            md_bg_color: 0.18, 0.49, 0.20, 1

        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            padding: "8dp"
            spacing: "8dp"

            MDRaisedButton:
                text: "New Entry"
                icon: "plus"
                on_release: root.open_add_dialog()

            MDRaisedButton:
                text: "Export"
                icon: "download"
                md_bg_color: 0.30, 0.30, 0.30, 1
                on_release: root.export_register()

        BoxLayout:
            id: table_holder
"""

Builder.load_string(KV)


class BankRegisterScreen(MDScreen):
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
        entries = db.get_bank_transactions()
        rows = [
            (str(e["s_no"]), self._display_date(e["date"]), str(e["total_bills"]),
             f'{e["total_credited"]:.2f}', f'{e["total_debited"]:.2f}', f'{e["balance"]:.2f}')
            for e in entries
        ]
        table = MDDataTable(
            size_hint=(1, 1), check=False,
            column_data=[
                ("S.No", dp(18)), ("Date", dp(28)), ("Total Bills", dp(24)),
                ("Credited (Rs.)", dp(30)), ("Debited (Rs.)", dp(30)), ("Balance (Rs.)", dp(30)),
            ],
            row_data=rows,
        )
        holder.add_widget(table)

    def open_add_dialog(self):
        self.picked_date = date.today()
        self.date_btn = MDFlatButton(text=f"Date: {self.picked_date.strftime('%d/%m/%Y')}",
                                      on_release=self.open_calendar)
        self.bills_field = MDTextField(hint_text="Total No. of Bills", input_filter="int")
        self.credit_field = MDTextField(hint_text="Total Amount Credited (Rs.)", input_filter="float")
        self.debit_field = MDTextField(hint_text="Total Amount Debited (Rs.)", input_filter="float")

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(260))
        for w in (self.date_btn, self.bills_field, self.credit_field, self.debit_field):
            content.add_widget(w)

        self.dialog = MDDialog(
            title="New Bank Transaction Entry",
            type="custom", content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SAVE", on_release=self.save_entry),
            ],
        )
        self.dialog.open()

    def open_calendar(self, instance):
        picker = MDModalDatePicker(sel_year=self.picked_date.year,
                                    sel_month=self.picked_date.month,
                                    sel_day=self.picked_date.day)
        picker.bind(on_ok=self._on_date_ok, on_cancel=lambda x: picker.dismiss())
        picker.open()

    def _on_date_ok(self, instance):
        sel = instance.get_date()[0]
        self.picked_date = sel
        self.date_btn.text = f"Date: {sel.strftime('%d/%m/%Y')}"
        instance.dismiss()

    def save_entry(self, *args):
        db.add_bank_transaction(
            self.picked_date.isoformat(),
            int(self.bills_field.text or 0),
            float(self.credit_field.text or 0),
            float(self.debit_field.text or 0),
        )
        toast("Bank entry saved")
        self.dialog.dismiss()
        self.refresh_table()

    def export_register(self):
        from utils.pdf_export import export_to_pdf
        entries = db.get_bank_transactions()
        rows = [
            [e["s_no"], self._display_date(e["date"]), e["total_bills"],
             f'{e["total_credited"]:.2f}', f'{e["total_debited"]:.2f}', f'{e["balance"]:.2f}']
            for e in entries
        ]
        path = export_to_pdf(
            "Bank Transaction Register",
            ["S.No", "Date", "Total Bills", "Credited", "Debited", "Balance"],
            rows,
        )
        toast(f"Saved to {path}")
