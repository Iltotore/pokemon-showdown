import kivy
from kivy.app import Builder, App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.window.window_sdl2 import WindowSDL
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.app import MDApp

from api import ShowdownApp
from api.concurrency import *
from graphics import screen_size

kivy.require('2.0.0')


def adapt_window(window: WindowSDL, size_coef):
    size = screen_size()
    if size is None:
        window.fullscreen = True
    else:
        window.size = size[0] * size_coef[0], size[1] * size_coef[1]
        window.left, window.top = size[0] * (0.5 - size_coef[0] / 2), size[1] * (0.5 - size_coef[1] / 2)


class ShowdownScreen(Screen):

    def __init__(self, **kw):
        App.get_running_app().web_app.add_dispatcher(self)
        super().__init__(**kw)


class SplashScreen(Screen):
    pass


class ClientScreen(ShowdownScreen):

    def __init__(self, **kw):
        self.register_event_type("on_mouse_pos")
        super().__init__(**kw)
        Window.bind(mouse_pos=lambda w, pos: self.dispatch("on_mouse_pos", pos))

    def on_mouse_pos(self, pos):
        pass


class DashboardScreen(ShowdownScreen):
    pass


class MainApp(MDApp):

    def __init__(self):
        super(MainApp, self).__init__()
        self.title = "Pokemon Showdown"
        self.icon = "misc/favicon.png"
        Builder.load_file("activity/main.kv")
        self.web_app = ShowdownApp()
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(SplashScreen(name="splash"))
        self.sm.add_widget(ClientScreen(name="client"))

    def build(self):
        Clock.schedule_once(lambda *args: self.sm.switch_to(app.sm.get_screen("client"), duration=0.5), 2)
        self.web_app.add_dispatcher(self.sm)
        return self.sm

    def on_stop(self):
        self.web_app.alive = False


if __name__ == '__main__':
    adapt_window(Window, (0.75, 0.75))
    app = MainApp()
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(app.async_run(),
                       worker_while(
                           TaskQueue(tasks=[lambda: app.web_app.listen()]),
                           lambda: app.web_app.alive, on_start=app.web_app.open(), on_stop=app.web_app.close()
                       ),
                       worker_while(
                           app.web_app.send_queue,
                           lambda: app.web_app.alive, on_start=wait_for(lambda: app.web_app.alive)
                       ))
    )
