from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.metrics import dp
import sqlite3
import subprocess
import sys

Window.clearcolor = (0, 0, 0, 1)
Window.size = (900, 600)

DB_PATH = "ecostar_pro.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        email TEXT)''')
    conn.commit()
    conn.close()


def register_user(username, password, name, email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, name, email) VALUES (?, ?, ?, ?)",
                  (username, password, name, email))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


# 🌈 Animated eco-gradient background
class AnimatedGradient(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.color_instruction = Color(0.0, 0.3, 0.1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.step = 0
        Clock.schedule_interval(self.animate, 0.05)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def animate(self, dt):
        self.step += 0.008
        offset = abs((self.step % 2) - 1)
        r = (0.0 * (1 - offset)) + (0.18 * offset)
        g = (0.4 * (1 - offset)) + (0.75 * offset)
        b = (0.1 * (1 - offset)) + (0.25 * offset)
        self.color_instruction.rgba = (r, g, b, 1)


# 💠 Glassmorphic container
class GlassCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical',
                         padding=dp(28), spacing=dp(12),
                         size_hint=(None, None),
                         size=(dp(420), dp(500)), **kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 0.1)
            self.bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(26)])
            Color(1, 1, 1, 0.25)
            self.border = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(26)], width=1.4)
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_graphics(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.pos = self.pos
        self.border.size = self.size


# 🌿 Main Register Page
class RegisterPage(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        create_tables()

        # Animated background
        self.bg = AnimatedGradient()
        self.add_widget(self.bg)

        # Glassmorphic card
        self.card = GlassCard(pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.add_widget(self.card)

        # Title
        self.card.add_widget(Label(
            text="[b]Create New Account[/b]",
            markup=True, font_size=34,
            color=(1, 1, 1, 0.95),
            size_hint=(1, None), height=50
        ))

        # Subtitle
        self.card.add_widget(Label(
            text="Join EcoStar Pro and start your sustainable journey 🌱",
            font_size=14, italic=True,
            color=(1, 1, 1, 0.75),
            size_hint=(1, None), height=26
        ))

        # Fields
        self.entries = {}
        fields = ["Username", "Password", "Full Name", "Email"]

        for field in fields:
            self.card.add_widget(Label(text=field, font_size=16, color=(1, 1, 1, 0.8), size_hint=(1, None), height=22))
            entry = TextInput(
                multiline=False, font_size=16, size_hint=(1, None), height=44,
                password=(field == "Password"),
                background_normal='', background_color=(1, 1, 1, 0.12),
                foreground_color=(1, 1, 1, 1), cursor_color=(1, 1, 1, 1),
                padding=[10, 10, 10, 10]
            )
            self.entries[field] = entry
            self.card.add_widget(entry)

        # Register button
        reg_btn = Button(
            text="Register", size_hint=(1, None), height=46,
            font_size=18, bold=True,
            background_normal='', background_color=(0.05, 0.55, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        reg_btn.bind(on_release=self.register)
        self.card.add_widget(reg_btn)

        # “Already have account?” text
        self.card.add_widget(Label(
            text="Already have an account?",
            font_size=14, color=(1, 1, 1, 0.75),
            size_hint=(1, None), height=22
        ))

        # Go to login button
        login_btn = Button(
            text="Go to Login", size_hint=(1, None), height=42,
            font_size=16, background_normal='',
            background_color=(0.2, 0.7, 0.25, 1),
            color=(1, 1, 1, 1)
        )
        login_btn.bind(on_release=self.back_to_login)
        self.card.add_widget(login_btn)

        # Smooth pop-in animation
        self.card.opacity = 0
        self.card.scale = 0.9
        Animation(opacity=1, scale=1, duration=1.0, t='out_elastic').start(self.card)

    def show_popup(self, title, msg):
        popup = Popup(
            title=title,
            content=Label(text=msg, font_size=16, color=(0, 0, 0, 1)),
            size_hint=(None, None), size=(400, 180),
            separator_color=(0, 0.5, 0.2, 1),
            title_color=(0, 0.5, 0.2, 1)
        )
        popup.open()

    def register(self, instance):
        username = self.entries["Username"].text.strip()
        password = self.entries["Password"].text.strip()
        name = self.entries["Full Name"].text.strip()
        email = self.entries["Email"].text.strip()

        if not all([username, password, name, email]):
            self.show_popup("Input Error", "Please fill all fields.")
            return

        if register_user(username, password, name, email):
            self.show_popup("Success", "Account created successfully!")
            self.back_to_login(instance)
        else:
            self.show_popup("Error", "Username already exists, try another.")

    def back_to_login(self, instance):
        App.get_running_app().stop()
        subprocess.Popen([sys.executable, "LoginPage.py"])


class RegisterApp(App):
    def build(self):
        return RegisterPage()


if __name__ == "__main__":
    RegisterApp().run()
