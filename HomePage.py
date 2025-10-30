import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

DB_PATH = "ecostar_pro.db"

def create_consumption_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            electricity REAL DEFAULT 0,
            water REAL DEFAULT 0,
            gas REAL DEFAULT 0,
            entry_date DATE DEFAULT (DATE('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_missing_columns():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    columns_to_add = [
        ("oil", "REAL DEFAULT 0"),
        ("cng", "REAL DEFAULT 0"),
        ("petrol", "REAL DEFAULT 0")
    ]

    for column, datatype in columns_to_add:
        try:
            c.execute(f"ALTER TABLE consumption ADD COLUMN {column} {datatype}")
        except sqlite3.OperationalError:
            # Column already exists, skip
            pass

    conn.commit()
    conn.close()

create_consumption_table()
add_missing_columns()


class DrawerApp(BoxLayout):
    def __init__(self, user_id, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        Window.clearcolor = (0.937, 0.98, 0.941, 1)  # #effaf0

        self.user_id = user_id

        self.drawer = BoxLayout(orientation='vertical', size_hint=(None, 1), width=180, spacing=8, padding=4)
        self.drawer_canvas_color()
        self.add_widget(self.drawer)

        btn_home = Button(text="Home", background_color=(0.22, 0.56, 0.24, 1), color=(1, 1, 1, 1),
                          font_size=15, size_hint=(1, None), height=46)
        btn_home.bind(on_release=self.show_home)
        self.drawer.add_widget(btn_home)

        btn_profile = Button(text="User Profile", background_color=(0.22, 0.56, 0.24, 1), color=(1, 1, 1, 1),
                             font_size=15, size_hint=(1, None), height=46)
        btn_profile.bind(on_release=self.show_profile)
        self.drawer.add_widget(btn_profile)

        btn_settings = Button(text="Settings", background_color=(0.22, 0.56, 0.24, 1), color=(1, 1, 1, 1),
                              font_size=15, size_hint=(1, None), height=46)
        btn_settings.bind(on_release=self.show_settings)
        self.drawer.add_widget(btn_settings)

        self.drawer.add_widget(Label(size_hint=(1, None), height=32))  # Spacer

        self.drawer.add_widget(Label(text="Analysis Time:", font_size=15, color=(1, 1, 1, 1),
                                     bold=True, size_hint=(1, None), height=20))

        self.analysis_time_var = "Daily"
        self.spinner = Spinner(
            text="Daily",
            values=["Daily", "Weekly", "Monthly"],
            size_hint=(1, None), height=36,
            background_color=(1, 1, 1, 1), color=(0, 0, 0, 1), font_size=14
        )
        self.spinner.bind(text=self.analysis_time_changed)
        self.drawer.add_widget(self.spinner)
        self.drawer.add_widget(Label(size_hint=(1, None), height=200))  # Filler

        btn_logout = Button(
            text="Logout",
            background_color=(0.72, 0.11, 0.11, 1),
            color=(1, 1, 1, 1), font_size=15, bold=True, size_hint=(1, None), height=46
        )
        btn_logout.bind(on_release=self.logout)
        self.drawer.add_widget(btn_logout)

        self.main_content = BoxLayout(orientation='vertical', padding=30, spacing=10)
        self.add_widget(self.main_content)

        self.load_user_data()

       


        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.scrollview import ScrollView

        scroll = ScrollView(size_hint=(1, None), size=(Window.width, 300))  # You can adjust height
        grid = GridLayout(cols=2, spacing=8, size_hint_y=None, padding=[10, 10])
        grid.bind(minimum_height=grid.setter("height"))

        types = [
            ("Electricity ⚡", "Electricity"),
            ("Oil 🛢️", "Oil"),
            ("Gas 🔥", "Gas"),
            ("CNG 🚗", "CNG"),
            ("Petrol ⛽", "Petrol"),
        ]

        for label_text, t in types:
            btn = Button(
                text=label_text,
                size_hint_y=None,
                height=50,
                background_color=(0.18, 0.49, 0.2, 1),
                color=(1, 1, 1, 1),
                font_size=16,
                bold=True
            )
            btn.bind(on_release=lambda instance, tp=t: self.open_add_consumption_popup(instance, tp))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        self.main_content.add_widget(scroll)

    def drawer_canvas_color(self):
        with self.drawer.canvas.before:
            Color(0.18, 0.49, 0.2, 1)  # #2e7d32
            self._rect = Rectangle(pos=self.drawer.pos, size=self.drawer.size)
            self.drawer.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self._rect.pos = instance.pos
        self._rect.size = instance.size

    def clear_main(self):
        self.main_content.clear_widgets()

    def show_home(self, *args):
        self.load_user_data()


    def show_profile(self, *args):
        self.clear_main()
        label = Label(text="User Profile Page\n(Details to be implemented)", font_size=18, color=(0.18, 0.49, 0.2, 1))
        self.main_content.add_widget(label)

    def show_settings(self, *args):
        self.clear_main()
        label = Label(text="Settings Page\n(Options to be implemented)", font_size=18, color=(0.18, 0.49, 0.2, 1))
        self.main_content.add_widget(label)

    def show_consumption_input(self, *args):
        self.clear_main()
        label = Label(
            text="Enter your power consumption (kWh):",
            font_size=20, color=(0.18, 0.49, 0.2, 1)
        )
        self.main_content.add_widget(label)

        # Input field
        self.electricity_input = TextInput(
            multiline=False, input_filter='float',
            size_hint=(1, None), height=40
        )
        self.main_content.add_widget(self.electricity_input)

        # Save button
        save_btn = Button(
            text="Save Consumption", size_hint=(1, None), height=44,
            background_color=(0.18, 0.49, 0.2, 1), color=(1, 1, 1, 1)
        )
        save_btn.bind(on_release=self.save_consumption)
        self.main_content.add_widget(save_btn)


    def save_consumption(self, instance):
        try:
            val = float(self.electricity_input.text.strip())
        except ValueError:
            self.show_info_popup("Invalid Input", "Please enter a valid number for electricity consumption.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO consumption (user_id, electricity) VALUES (?, ?)",
            (self.user_id, val)
        )
        conn.commit()
        conn.close()

        self.show_info_popup("Success", "Consumption data saved successfully!")
        self.show_home()


    def analysis_time_changed(self, spinner, val):
        self.analysis_time_var = val
        self.show_info_popup("Analysis Time Changed", f"Selected: {val}")
        if val == 'Daily':
            self.show_consumption_input()
        else:
            self.show_home()


    def logout(self, instance):
        content = BoxLayout(orientation='vertical', padding=12, spacing=8)
        content.add_widget(Label(text="Do you want to logout?", font_size=17))
        btns = BoxLayout(spacing=12, size_hint=(1, None), height=44)
        yes_btn = Button(text="Yes", background_color=(0.72, 0.11, 0.11, 1), color=(1,1,1,1))
        no_btn = Button(text="No", background_color=(0.18, 0.49, 0.2, 1), color=(1,1,1,1))
        btns.add_widget(yes_btn)
        btns.add_widget(no_btn)
        content.add_widget(btns)
        popup = Popup(title="Logout", content=content, size_hint=(None,None), size=(320, 170))
        yes_btn.bind(on_release=lambda *a: (popup.dismiss(), App.get_running_app().stop()))
        no_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_info_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg, font_size=16), size_hint=(None,None), size=(320, 140))
        popup.open()

    def open_add_consumption_popup(self, instance, consumption_type):
        content = BoxLayout(orientation='vertical', padding=12, spacing=8)

        label = Label(text=f"Enter {consumption_type} usage:", font_size=16, color=(0, 0, 0, 1))
        usage_input = TextInput(multiline=False, input_filter='float', size_hint=(1, None), height=40)
        content.add_widget(label)
        content.add_widget(usage_input)

        btns = BoxLayout(size_hint=(1, None), height=44, spacing=8)
        save_btn = Button(text="Save", background_color=(0.18, 0.49, 0.2, 1), color=(1, 1, 1, 1))
        cancel_btn = Button(text="Cancel", background_color=(0.72, 0.11, 0.11, 1), color=(1, 1, 1, 1))
        btns.add_widget(save_btn)
        btns.add_widget(cancel_btn)
        content.add_widget(btns)

        popup = Popup(title=f"Add {consumption_type}", content=content, size_hint=(None, None), size=(340, 220))

        def save_and_close(*args):
            try:
                val = float(usage_input.text.strip())
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
            # Dynamically insert based on type
                c.execute(f"UPDATE consumption SET {consumption_type.lower()} = ? WHERE user_id = ?", (val, self.user_id))
                conn.commit()
                conn.close()
                popup.dismiss()
                self.show_info_popup("Success", f"{consumption_type} data added!")
                self.load_user_data()
            except ValueError:
                self.show_info_popup("Error", "Invalid input. Please enter a number.")

        save_btn.bind(on_release=save_and_close)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    # New Methods to integrate user data

    def get_user_details(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, name, email FROM users WHERE id=?", (self.user_id,))
        user = c.fetchone()
        conn.close()
        return user if user else (None, None, None)

    def load_user_data(self):
        username, name, email = self.get_user_details()
        self.clear_main()

        if username:
            welcome_label = Label(
                text=f"Welcome back, [b]{name or username}[/b]!",
                markup=True,
                font_size=24,
                color=(0.18, 0.49, 0.2, 1),
                size_hint=(1, None),
                height=60
            )
            self.main_content.add_widget(welcome_label)

        # 🟩 Consumption summary
        consumption_summary = self.get_latest_consumption_summary()
        summary_label = Label(
            text=consumption_summary,
            font_size=18,
            color=(0.3, 0.5, 0.3, 1),
            size_hint=(1, None),
            height=50
        )
        self.main_content.add_widget(summary_label)

       


    def get_latest_consumption_summary(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT SUM(electricity), SUM(water), SUM(gas) FROM consumption WHERE user_id=?""", (self.user_id,))
        data = c.fetchone()
        conn.close()
        if data:
            elec, water, gas = data
            elec, water, gas = elec or 0, water or 0, gas or 0
            return f"Consumption Summary: Electricity: {elec} kWh, Water: {water} L, Gas: {gas} m3"
        else:
            return "No consumption data found."


class HomePageApp(App):
    def build(self):
        # Replace with actual logged-in user ID in real use
        return DrawerApp(user_id=1)


if __name__ == "__main__":
    HomePageApp().run()
