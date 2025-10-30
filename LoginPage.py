from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.metrics import dp
import sqlite3
import subprocess
import sys

# 🌿 Global setup
Window.size = (950, 600)
Window.clearcolor = (0, 0, 0, 1)

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


def get_user_id(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None


# 🌈 Modern animated gradient background
class AnimatedGradient(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.color_instruction = Color(0.0, 0.25, 0.1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.step = 0
        Clock.schedule_interval(self.animate, 0.05)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def animate(self, dt):
        self.step += 0.005
        offset = abs((self.step % 2) - 1)
        r = 0.05 + 0.15 * offset
        g = 0.4 + 0.4 * offset
        b = 0.1 + 0.15 * offset
        self.color_instruction.rgba = (r, g, b, 1)


# 💠 Glass card with blur and shadow illusion
class GlassCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(36), spacing=dp(20),
                         size_hint=(None, None), size=(dp(440), dp(500)), **kwargs)
        with self.canvas.before:
            # Background layer (semi-transparent)
            Color(1, 1, 1, 0.1)
            self.bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(28)])
            # Border light layer
            Color(1, 1, 1, 0.25)
            self.border = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(28)])
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_graphics(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.pos = self.pos
        self.border.size = self.size


# 🌿 Modern Login Page
class LoginPage(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Background animation
        self.bg = AnimatedGradient()
        self.add_widget(self.bg)

        # Glass card
        self.card = GlassCard(pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.add_widget(self.card)

        # Title
        title = Label(
            text="[b]EcoStar Pro[/b]",
            markup=True,
            font_size=46,
            color=(1, 1, 1, 0.95),
            size_hint=(1, None),
            height=70,
        )
        subtitle = Label(
            text="Sustainability Starts With You.",
            font_size=18,
            italic=True,
            color=(1, 1, 1, 0.7),
            size_hint=(1, None),
            height=30,
        )
        self.card.add_widget(title)
        self.card.add_widget(subtitle)

        # Username Input
        self.card.add_widget(Label(text="Username", font_size=17, color=(1, 1, 1, 0.85)))
        self.username_entry = TextInput(
            multiline=False,
            font_size=17,
            size_hint=(1, None),
            height=48,
            background_normal='',
            background_color=(1, 1, 1, 0.12),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[12, 12, 12, 12]
        )
        self.card.add_widget(self.username_entry)

        # Password Input
        self.card.add_widget(Label(text="Password", font_size=17, color=(1, 1, 1, 0.85)))
        self.password_entry = TextInput(
            multiline=False,
            password=True,
            font_size=17,
            size_hint=(1, None),
            height=48,
            background_normal='',
            background_color=(1, 1, 1, 0.12),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            padding=[12, 12, 12, 12]
        )
        self.card.add_widget(self.password_entry)

        # Login Button
        self.login_btn = Button(
            text="Sign In",
            size_hint=(1, None),
            height=52,
            font_size=20,
            bold=True,
            background_normal='',
            background_color=(0.1, 0.6, 0.25, 1),
            color=(1, 1, 1, 1),
        )
        self.login_btn.bind(on_release=self.login)
        self.card.add_widget(self.login_btn)

        # “Don’t have account?”
        self.card.add_widget(Label(
            text="Don’t have an account?",
            font_size=15,
            color=(1, 1, 1, 0.7),
            size_hint=(1, None),
            height=26
        ))

        # Register Button
        self.register_btn = Button(
            text="Create Account",
            size_hint=(1, None),
            height=46,
            font_size=18,
            background_normal='',
            background_color=(0.2, 0.75, 0.35, 1),
            color=(1, 1, 1, 1)
        )
        self.register_btn.bind(on_release=self.open_register)
        self.card.add_widget(self.register_btn)

        # Animation
        self.card.opacity = 0
        self.card.scale = 0.9
        Animation(opacity=1, scale=1, duration=1.1, t='out_elastic').start(self.card)

    def show_popup(self, title, msg):
        popup = Popup(
            title=title,
            content=Label(text=msg, font_size=18, color=(0, 0, 0, 1)),
            size_hint=(None, None),
            size=(400, 180),
            separator_color=(0, 0.5, 0.2, 1),
            title_color=(0, 0.5, 0.2, 1)
        )
        popup.open()

    def login(self, instance):
        username = self.username_entry.text.strip()
        password = self.password_entry.text.strip()
        if not username or not password:
            self.show_popup("Input Error", "Please enter both username and password.")
            return
        user_id = get_user_id(username, password)
        if user_id:
            self.show_popup("Success", f"Welcome, {username}!")
            App.get_running_app().stop()
            subprocess.Popen([sys.executable, "HomePage.py", str(user_id)])
        else:
            self.show_popup("Failed", "Invalid username or password.")

    def open_register(self, instance):
        App.get_running_app().stop()
        subprocess.Popen([sys.executable, "RegisterPage.py"])


class LoginApp(App):
    def build(self):
        return LoginPage()


if __name__ == "__main__":
    LoginApp().run()
