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
<DailySalesScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Daily Sales Register"
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


class DailySalesScreen(MDScreen):
    dialog = None
    picked_date = None

    def on_pre_enter(self, *args):
        self.refresh_table()

    def go_back(self):
        self.manager.current = "dashboard"

    def refresh_table(self):
        holder = self.ids.table_holder
        holder.clear_widgets()
        entries = db.get_daily_sales()
        rows = [
            (str(e["s_no"]), self._display_date(e["date"]), e["bill_from"] or "-",
             e["bill_to"] or "-", f'{e["total_amount"]:.2f}', (e["remarks"] or "")[:40])
            for e in entries
        ]
        table = MDDataTable(
            size_hint=(1, 1),
            check=False,
            column_data=[
                ("S.No", dp(20)), ("Date", dp(30)), ("Bill From", dp(30)),
                ("Bill To", dp(30)), ("Total (Rs.)", dp(30)), ("Remarks", dp(50)),
            ],
            row_data=rows,
        )
        holder.add_widget(table)

    @staticmethod
    def _display_date(iso):
        y, m, d = iso.split("-")
        return f"{d}/{m}/{y}"

    def open_add_dialog(self):
        self.picked_date = date.today()
        self.date_btn = MDFlatButton(
            text=f"Date: {self.picked_date.strftime('%d/%m/%Y')}",
            on_release=self.open_calendar,
        )
        self.bill_from_field = MDTextField(hint_text="Bill No. From")
        self.bill_to_field = MDTextField(hint_text="Bill No. To")
        self.total_field = MDTextField(hint_text="Total Amount Credited (Rs.)", input_filter="float")
        self.remarks_field = MDTextField(hint_text="Remarks (max 150 chars)", max_text_length=150)

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(300))
        for w in (self.date_btn, self.bill_from_field, self.bill_to_field,
                  self.total_field, self.remarks_field):
            content.add_widget(w)

        self.dialog = MDDialog(
            title="New Daily Sales Entry\n(enter even if total is zero)",
            type="custom",
            content_cls=content,
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
        total = float(self.total_field.text or 0)
        db.add_daily_sales(
            self.picked_date.isoformat(),
            self.bill_from_field.text.strip(),
            self.bill_to_field.text.strip(),
            total,
            self.remarks_field.text.strip(),
        )
        toast("Entry saved")
        self.dialog.dismiss()
        self.refresh_table()

    def export_register(self):
        from utils.pdf_export import export_to_pdf
        entries = db.get_daily_sales()
        rows = [
            [e["s_no"], self._display_date(e["date"]), e["bill_from"], e["bill_to"],
             f'{e["total_amount"]:.2f}', e["remarks"]]
            for e in entries
        ]
        path = export_to_pdf(
            "Daily Sales Register",
            ["S.No", "Date", "Bill From", "Bill To", "Total Amount Credited", "Remarks"],
            rows,
        )
        toast(f"Saved to {path}")
