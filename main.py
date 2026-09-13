"""
Eco Shop Register App
Anamalai Tiger Reserve, Pollachi Division, Tamil Nadu Forest Department
------------------------------------------------------------------------
Built with Kivy + KivyMD. SQLite backend (database.py) stores all 5
registers plus the product master with auto-generated unique product codes.
"""

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

import database as db

from screens.dashboard import DashboardScreen
from screens.products import ProductsScreen
from screens.daily_sales import DailySalesScreen
from screens.cash_register import CashRegisterScreen
from screens.purchase_register import PurchaseRegisterScreen
from screens.stock_register import StockRegisterScreen
from screens.bank_register import BankRegisterScreen


class EcoShopApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Light"
        self.title = "Eco Shop — Anamalai Tiger Reserve"

        db.init_db()

        sm = MDScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ProductsScreen(name="products"))
        sm.add_widget(DailySalesScreen(name="daily_sales"))
        sm.add_widget(CashRegisterScreen(name="cash_register"))
        sm.add_widget(PurchaseRegisterScreen(name="purchase_register"))
        sm.add_widget(StockRegisterScreen(name="stock_register"))
        sm.add_widget(BankRegisterScreen(name="bank_register"))
        return sm


if __name__ == "__main__":
    EcoShopApp().run()
