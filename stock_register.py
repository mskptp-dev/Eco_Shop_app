from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.toast import toast
from datetime import date

import database as db

KV = """
<StockRegisterScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Stock Register"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 4
            md_bg_color: 0.18, 0.49, 0.20, 1

        MDBoxLayout:
            size_hint_y: None
            height: "48dp"
            padding: "8dp", "0dp"

            MDSegmentedControl:
                id: view_switch
                on_active: root.on_view_switch(*args)

                MDSegmentedControlItem:
                    text: "Current Stock"

                MDSegmentedControlItem:
                    text: "Day-wise Stock"

        MDBoxLayout:
            id: nav_bar
            size_hint_y: None
            height: "48dp"
            padding: "8dp"
            spacing: "8dp"
            opacity: 0
            disabled: True

            MDIconButton:
                icon: "chevron-left"
                on_release: root.shift_day(-1)

            MDFlatButton:
                id: date_label
                text: "Today"
                on_release: root.open_calendar()

            MDIconButton:
                icon: "chevron-right"
                on_release: root.shift_day(1)

            Widget:

            MDRaisedButton:
                text: "Export"
                icon: "download"
                md_bg_color: 0.30, 0.30, 0.30, 1
                on_release: root.export_current_view()

        BoxLayout:
            id: table_holder
"""

Builder.load_string(KV)


class StockRegisterScreen(MDScreen):
    current_view_date = None
    mode = "current"  # or "daywise"

    def on_pre_enter(self, *args):
        self.current_view_date = date.today()
        # freeze today's snapshot so day-wise history stays accurate
        db.record_daily_stock_snapshot(self.current_view_date.isoformat())
        self.show_current_stock()

    def go_back(self):
        self.manager.current = "dashboard"

    def on_view_switch(self, instance, value):
        if value == "Current Stock":
            self.mode = "current"
            self.ids.nav_bar.opacity = 0
            self.ids.nav_bar.disabled = True
            self.show_current_stock()
        else:
            self.mode = "daywise"
            self.ids.nav_bar.opacity = 1
            self.ids.nav_bar.disabled = False
            self.current_view_date = date.today()
            self.ids.date_label.text = self.current_view_date.strftime("%d/%m/%Y")
            self.show_daywise_stock()

    def show_current_stock(self):
        holder = self.ids.table_holder
        holder.clear_widgets()
        products = db.get_current_stock()
        rows = [
            (p["code"], p["name"], p["category"], f'{p["current_stock"]:.2f} {p["unit"]}')
            for p in products
        ]
        table = MDDataTable(
            size_hint=(1, 1), check=False,
            column_data=[("Code", dp(26)), ("Name", dp(50)), ("Category", dp(28)), ("Current Stock", dp(34))],
            row_data=rows,
        )
        holder.add_widget(table)

    def show_daywise_stock(self):
        holder = self.ids.table_holder
        holder.clear_widgets()
        rows_data = db.get_daywise_stock(self.current_view_date.isoformat())
        rows = [
            (r["name"], f'{r["initial_stock"]:.2f}', f'{r["sold_quantity"]:.2f}', f'{r["balance_stock"]:.2f} {r["unit"]}')
            for r in rows_data
        ]
        table = MDDataTable(
            size_hint=(1, 1), check=False,
            column_data=[("Product", dp(40)), ("Initial Stock", dp(30)), ("Sold Qty", dp(30)), ("Balance Stock", dp(34))],
            row_data=rows,
        )
        holder.add_widget(table)

    def shift_day(self, delta):
        from datetime import timedelta
        self.current_view_date += timedelta(days=delta)
        self.ids.date_label.text = self.current_view_date.strftime("%d/%m/%Y")
        self.show_daywise_stock()

    def open_calendar(self):
        picker = MDModalDatePicker(sel_year=self.current_view_date.year,
                                    sel_month=self.current_view_date.month,
                                    sel_day=self.current_view_date.day)
        picker.bind(on_ok=self._on_date_ok, on_cancel=lambda x: picker.dismiss())
        picker.open()

    def _on_date_ok(self, instance):
        sel = instance.get_date()[0]
        self.current_view_date = sel
        self.ids.date_label.text = sel.strftime("%d/%m/%Y")
        self.show_daywise_stock()
        instance.dismiss()

    def export_current_view(self):
        from utils.pdf_export import export_to_pdf
        if self.mode == "current":
            products = db.get_current_stock()
            rows = [[p["code"], p["name"], p["category"], f'{p["current_stock"]:.2f} {p["unit"]}'] for p in products]
            path = export_to_pdf("Current Stock Register", ["Code", "Name", "Category", "Current Stock"], rows)
        else:
            rows_data = db.get_daywise_stock(self.current_view_date.isoformat())
            rows = [[r["name"], f'{r["initial_stock"]:.2f}', f'{r["sold_quantity"]:.2f}',
                     f'{r["balance_stock"]:.2f} {r["unit"]}'] for r in rows_data]
            path = export_to_pdf(
                f"Stock Register {self.current_view_date.strftime('%d-%m-%Y')}",
                ["Product", "Initial Stock", "Sold Qty", "Balance Stock"], rows,
            )
        toast(f"Saved to {path}")
