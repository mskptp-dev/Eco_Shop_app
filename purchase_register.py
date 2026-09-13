from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.toast import toast
from datetime import date

import database as db

KV = """
<PurchaseRegisterScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Purchase Register"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 4
            md_bg_color: 0.18, 0.49, 0.20, 1

        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            padding: "8dp"
            spacing: "8dp"

            MDRaisedButton:
                text: "New Purchase"
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


class PurchaseRegisterScreen(MDScreen):
    dialog = None
    picked_date = None
    selected_category = "GROCERY"
    selected_product = None

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
        entries = db.get_purchases()
        rows = [
            (str(e["s_no"]), self._display_date(e["date"]), e["purchase_bill_no"] or "-",
             e["vendor_name"] or "-", e["category"], e["item_name"] or "-",
             f'{e["quantity"]:.2f} {e["unit"]}', f'{e["total_amount"]:.2f}')
            for e in entries
        ]
        table = MDDataTable(
            size_hint=(1, 1),
            check=False,
            column_data=[
                ("S.No", dp(16)), ("Date", dp(26)), ("Bill No.", dp(24)),
                ("Vendor", dp(30)), ("Type", dp(22)), ("Item", dp(30)),
                ("Qty", dp(24)), ("Amount (Rs.)", dp(26)),
            ],
            row_data=rows,
        )
        holder.add_widget(table)

    def open_add_dialog(self):
        self.picked_date = date.today()
        self.date_btn = MDFlatButton(text=f"Date: {self.picked_date.strftime('%d/%m/%Y')}",
                                      on_release=self.open_calendar)
        self.bill_field = MDTextField(hint_text="Purchase Bill No.")
        self.vendor_field = MDTextField(hint_text="Vendor Name")

        self.category_btn = MDFlatButton(text="Type: GROCERY", on_release=self.open_category_menu)

        self.item_name_field = MDTextField(hint_text="Item name (e.g. Tea powder, T-shirt)")
        self.qty_field = MDTextField(hint_text="Quantity", input_filter="float")
        self.unit_btn = MDFlatButton(text="Unit: Kg", on_release=self.open_unit_menu)
        self.selected_unit = "Kg"

        self.total_field = MDTextField(hint_text="Total Amount (Rs.)", input_filter="float")
        self.remarks_field = MDTextField(hint_text="Remarks (max 150 chars)", max_text_length=150)
        self.link_stock_btn = MDFlatButton(
            text="Link to existing STOCK product? (optional)",
            on_release=self.open_product_menu,
        )

        content = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None, height=dp(480))
        for w in (self.date_btn, self.bill_field, self.vendor_field, self.category_btn,
                  self.item_name_field, self.qty_field, self.unit_btn,
                  self.link_stock_btn, self.total_field, self.remarks_field):
            content.add_widget(w)

        self.dialog = MDDialog(
            title="New Purchase Entry",
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

    def open_category_menu(self, instance):
        items = [
            {"text": "GROCERY", "on_release": lambda x="GROCERY": self.set_category(x)},
            {"text": "STOCK", "on_release": lambda x="STOCK": self.set_category(x)},
        ]
        MDDropdownMenu(caller=instance, items=items, width_mult=3).open()

    def set_category(self, value):
        self.selected_category = value
        self.category_btn.text = f"Type: {value}"

    def open_unit_menu(self, instance):
        items = [{"text": u, "on_release": lambda x=u: self.set_unit(x)} for u in ("Nos", "Kg", "Lt")]
        MDDropdownMenu(caller=instance, items=items, width_mult=3).open()

    def set_unit(self, value):
        self.selected_unit = value
        self.unit_btn.text = f"Unit: {value}"

    def open_product_menu(self, instance):
        products = db.get_products(category="STOCK")
        if not products:
            toast("No STOCK products yet — add one in Product Master first")
            return
        items = [
            {"text": f'{p["code"]} - {p["name"]}', "on_release": lambda p=p: self.set_product(p)}
            for p in products
        ]
        MDDropdownMenu(caller=instance, items=items, width_mult=4).open()

    def set_product(self, product):
        self.selected_product = product
        self.link_stock_btn.text = f'Linked: {product["code"]} - {product["name"]}'
        self.item_name_field.text = product["name"]

    def save_entry(self, *args):
        item_code = self.selected_product["code"] if self.selected_product else None
        db.add_purchase(
            self.picked_date.isoformat(),
            self.bill_field.text.strip(),
            self.vendor_field.text.strip(),
            self.selected_category,
            item_code,
            self.item_name_field.text.strip(),
            float(self.qty_field.text or 0),
            self.selected_unit,
            float(self.total_field.text or 0),
            self.remarks_field.text.strip(),
        )
        toast("Purchase entry saved" + (" — stock updated" if item_code else ""))
        self.dialog.dismiss()
        self.selected_product = None
        self.refresh_table()

    def export_register(self):
        from utils.pdf_export import export_to_pdf
        entries = db.get_purchases()
        rows = [
            [e["s_no"], self._display_date(e["date"]), e["purchase_bill_no"], e["vendor_name"],
             e["category"], e["item_name"], f'{e["quantity"]:.2f} {e["unit"]}',
             f'{e["total_amount"]:.2f}', e["remarks"]]
            for e in entries
        ]
        path = export_to_pdf(
            "Purchase Register",
            ["S.No", "Date", "Bill No.", "Vendor", "Type", "Item", "Quantity", "Amount", "Remarks"],
            rows,
        )
        toast(f"Saved to {path}")
