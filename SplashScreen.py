from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.core.window import Window
import subprocess
import sys

# Set larger window size
Window.size = (800, 400)

class ModernSplash(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint=(1, 1), **kwargs)

        # Gradient background
        with self.canvas.before:
            for i in range(80):
                t = i / 79.0
                r = 0 * (1 - t) + 0.196 * t
                g = 0.39 * (1 - t) + 0.803 * t
                b = 0 * (1 - t) + 0.196 * t
                Color(r, g, b)
                RoundedRectangle(pos=(0, i * (self.height / 80)), size=(self.width, self.height / 80))

        # Card container
        self.card = BoxLayout(
            orientation='vertical',
            padding=30,
            spacing=24,
            size_hint=(None, None),
            size=(700, 300),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        with self.card.canvas.before:
            Color(1, 1, 1, 0.14)
            self.bg = RoundedRectangle(size=self.card.size, pos=self.card.pos, radius=[30])
        self.card.bind(size=self.update_bg, pos=self.update_bg)
        self.add_widget(self.card)

        # Title
        self.title = Label(
            text="[b]EcoStar Pro[/b]",
            font_size=56,
            markup=True,
            color=(0.18, 0.49, 0.2, 1)
        )
        self.card.add_widget(self.title)

        # Tagline
        self.tagline = Label(
            text="Towards a Sustainable Future",
            font_size=28,
            italic=True,
            color=(0.17, 0.5, 0.27, 1)
        )
        self.card.add_widget(self.tagline)

        # Slogan
        self.slogan = Label(
            text="Save Energy   |   Save Water   |   Save Earth",
            font_size=22,
            color=(0.4, 0.8, 0.47, 1)
        )
        self.card.add_widget(self.slogan)

        # Fade-in animation
        for widget in self.card.children:
            widget.opacity = 0
            Animation(opacity=1, d=1.1, t='out_cubic').start(widget)

        # Schedule closing splash and launching login page
        Clock.schedule_once(self.launch_login, 4)

    def update_bg(self, *args):
        self.bg.pos = self.card.pos
        self.bg.size = self.card.size

    def launch_login(self, dt):
        App.get_running_app().stop()  # Close splash
        subprocess.Popen([sys.executable, "LoginPage.py"])  

class SplashApp(App):
    def build(self):
        return ModernSplash()

if __name__ == "__main__":
    SplashApp().run()
