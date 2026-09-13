from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

KV = """
<DashboardScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Eco Shop — Anamalai Tiger Reserve"
            elevation: 4
            md_bg_color: 0.18, 0.49, 0.20, 1

        ScrollView:
            MDGridLayout:
                cols: 2
                padding: "16dp"
                spacing: "16dp"
                adaptive_height: True

                DashTile:
                    icon: "cube-outline"
                    text: "Product\\nMaster"
                    on_release: root.go("products")

                DashTile:
                    icon: "cart-outline"
                    text: "Daily Sales\\nRegister"
                    on_release: root.go("daily_sales")

                DashTile:
                    icon: "cash-multiple"
                    text: "Cash\\nRegister"
                    on_release: root.go("cash_register")

                DashTile:
                    icon: "truck-delivery-outline"
                    text: "Purchase\\nRegister"
                    on_release: root.go("purchase_register")

                DashTile:
                    icon: "package-variant-closed"
                    text: "Stock\\nRegister"
                    on_release: root.go("stock_register")

                DashTile:
                    icon: "bank-outline"
                    text: "Bank Transaction\\nRegister"
                    on_release: root.go("bank_register")


<DashTile@MDCard>:
    icon: "help"
    text: ""
    orientation: "vertical"
    size_hint_y: None
    height: "140dp"
    padding: "12dp"
    spacing: "8dp"
    ripple_behavior: True
    elevation: 2
    radius: [16, 16, 16, 16]

    MDIcon:
        icon: root.icon
        halign: "center"
        font_size: "40dp"
        theme_text_color: "Custom"
        text_color: 0.18, 0.49, 0.20, 1

    MDLabel:
        text: root.text
        halign: "center"
        theme_text_color: "Primary"
"""

Builder.load_string(KV)


class DashboardScreen(MDScreen):
    def go(self, screen_name):
        self.manager.current = screen_name
