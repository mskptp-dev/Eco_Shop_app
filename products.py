from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast

import database as db

KV = """
<ProductsScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Product Master"
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            elevation: 4
            md_bg_color: 0.18, 0.49, 0.20, 1

        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            padding: "8dp"
            spacing: "8dp"

            MDRaisedButton:
                text: "Add Product"
                icon: "plus"
                on_release: root.open_add_dialog()

            MDRaisedButton:
                text: "Export List"
                icon: "download"
                md_bg_color: 0.30, 0.30, 0.30, 1
                on_release: root.export_products()

        BoxLayout:
            id: table_holder
"""

Builder.load_string(KV)


class ProductsScreen(MDScreen):
    dialog = None
    category_menu = None
    unit_menu = None
    selected_category = "STOCK"
    selected_unit = "Nos"

    def on_pre_enter(self, *args):
        self.refresh_table()

    def go_back(self):
        self.manager.current = "dashboard"

    def refresh_table(self):
        holder = self.ids.table_holder
        holder.clear_widgets()
        products = db.get_products()
        rows = [
            (p["code"], p["name"], p["category"], p["unit"], f'{p["price"]:.2f}', f'{p["current_stock"]:.2f}')
            for p in products
        ]
        table = MDDataTable(
            size_hint=(1, 1),
            check=False,
            column_data=[
                ("Code", dp(28)), ("Name", dp(48)), ("Category", dp(30)),
                ("Unit", dp(20)), ("Price", dp(24)), ("Stock", dp(24)),
            ],
            row_data=rows,
        )
        holder.add_widget(table)

    def open_add_dialog(self):
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.boxlayout import MDBoxLayout

        self.name_field = MDTextField(hint_text="Product name")
        self.price_field = MDTextField(hint_text="Price (Rs.)", input_filter="float")
        self.stock_field = MDTextField(hint_text="Opening stock", input_filter="float")

        self.category_btn = MDFlatButton(text="Category: STOCK", on_release=self.open_category_menu)
        self.unit_btn = MDFlatButton(text="Unit: Nos", on_release=self.open_unit_menu)

        content = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, height=dp(260))
        content.add_widget(self.name_field)
        content.add_widget(self.category_btn)
        content.add_widget(self.unit_btn)
        content.add_widget(self.price_field)
        content.add_widget(self.stock_field)

        self.dialog = MDDialog(
            title="Add Product",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="SAVE", on_release=self.save_product),
            ],
        )
        self.dialog.open()

    def open_category_menu(self, instance):
        items = [
            {"text": "STOCK", "on_release": lambda x="STOCK": self.set_category(x)},
            {"text": "GROCERY", "on_release": lambda x="GROCERY": self.set_category(x)},
        ]
        self.category_menu = MDDropdownMenu(caller=instance, items=items, width_mult=3)
        self.category_menu.open()

    def set_category(self, value):
        self.selected_category = value
        self.category_btn.text = f"Category: {value}"
        self.category_menu.dismiss()

    def open_unit_menu(self, instance):
        items = [
            {"text": u, "on_release": lambda x=u: self.set_unit(x)}
            for u in ("Nos", "Kg", "Lt")
        ]
        self.unit_menu = MDDropdownMenu(caller=instance, items=items, width_mult=3)
        self.unit_menu.open()

    def set_unit(self, value):
        self.selected_unit = value
        self.unit_btn.text = f"Unit: {value}"
        self.unit_menu.dismiss()

    def save_product(self, *args):
        name = self.name_field.text.strip()
        if not name:
            toast("Enter a product name")
            return
        price = float(self.price_field.text or 0)
        stock = float(self.stock_field.text or 0)
        code = db.add_product(name, self.selected_category, self.selected_unit, price, stock)
        toast(f"Added: {code}")
        self.dialog.dismiss()
        self.refresh_table()

    def export_products(self):
        from utils.pdf_export import export_to_pdf
        products = db.get_products()
        rows = [
            [p["code"], p["name"], p["category"], p["unit"], f'{p["price"]:.2f}', f'{p["current_stock"]:.2f}']
            for p in products
        ]
        path = export_to_pdf(
            "Product Master List",
            ["Code", "Name", "Category", "Unit", "Price", "Current Stock"],
            rows,
        )
        toast(f"Saved to {path}")
