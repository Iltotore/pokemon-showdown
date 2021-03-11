import kivy
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp

kivy.require('2.0.0')

from kivy.app import Builder

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition


class SplashScreen(Screen):
    pass


class DashboardScreen(Screen):
    pass


class MainApp(MDApp):

    def __init__(self):
        super(MainApp, self).__init__()
        self.sm = ScreenManager()

    def build(self):
        self.title = "Pokemon Showdown"
        self.icon = "assets/misc/favicon.png"
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(SplashScreen(name="splash"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        Clock.schedule_once(lambda *args: self.sm.switch_to(app.sm.get_screen("dashboard"), duration=1), 3)
        return self.sm


if __name__ == '__main__':
    print(Window.size)
    Builder.load_file("activity/main.kv")
    """Window.size = (900, 700)
    Window.left, Window.top = (0, 0)"""
    app = MainApp()
    app.run()
