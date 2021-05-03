from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget


class HoverBehaviour(Widget):
    hover = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.register_event_type("on_enter")
        self.register_event_type("on_exit")
        super(HoverBehaviour, self).__init__(**kwargs)

    def corners_abs(self):
        abs_x, abs_y = self.to_window(self.x, self.y)
        return abs_x, abs_y, abs_x + self.size[0], abs_y + self.size[1]

    def collide_abs(self, x, y):
        abs_x, abs_y, abs_right, abs_top = self.corners_abs()
        return abs_x <= x <= abs_right and abs_y <= y <= abs_top

    def update_mouse(self, x, y):
        if self.collide_abs(x, y):
            if not self.hover:
                self.dispatch("on_enter", x, y)
            self.hover = True
        else:
            if self.hover:
                self.dispatch("on_exit", x, y)
            self.hover = False

    def on_enter(self, widget, *args):
        pass

    def on_exit(self, widget, *args):
        pass


class Tab(OneLineIconListItem):
    icon = StringProperty("folder")

    def __init__(self, **kwargs):
        super(Tab, self).__init__(**kwargs)
        self.screen = None
        self.screen_manager = None
        self.icon_widget = IconLeftWidget(icon=self.icon)
        self.bind(icon=self.icon_widget.setter("icon"))
        Clock.schedule_once(self.on_start)

    def on_start(self, *args):
        self.add_widget(self.icon_widget)

    def on_press(self):
        if self.screen is not None and self.screen_manager is not None:
            self.screen_manager.switch_to(self.screen)


class CloseableTab(Tab, HoverBehaviour):

    def __init__(self, **kwargs):
        self.register_event_type("on_close_request")
        self.register_event_type("on_close")
        super(CloseableTab, self).__init__(**kwargs)
        self.closing = False
        self.icon_widget.bind(on_press=lambda w, *args: self.close())

    def on_enter(self, widget, *args):
        self.icon_widget.icon = "close"

    def on_exit(self, widget, *args):
        self.icon_widget.icon = self.icon

    def on_close_request(self, *args):
        pass

    def on_close(self, *args):
        pass

    def close(self, force=False):
        self.closing = True
        self.dispatch("on_close_request")
        if self.closing or force:
            self.dispatch("on_close")
            self.parent.remove_widget(self)


class FDDButton(Button):
    pass


class FilterDD(RelativeLayout, EventDispatcher):

    def __init__(self, buttons=(), **kwargs):
        super(FilterDD, self).__init__(**kwargs)

        self.register_event_type("on_item_select")
        self.entries = buttons
        self.selected = ""
        self.button_factory = lambda text: Factory.FDDButton(text=text)
        self.multiline = False

        self.orientation = "vertical"
        self.input_area = TextInput(size_hint=(1, 0.1))

        self.input_area.fbind("focus", self.on_focus)
        self.input_area.bind(text=self.update_text)
        self.input_area.bind(on_touch_down=self.on_touch_down)
        self.drop_down = DropDown()
        self.add_widget(self.input_area)
        self.add_widget(self.drop_down)

        self.drop_down.bind(on_dismiss=self.real_dismiss)
        self.drop_down.auto_dismiss = False
        self.auto_dismiss = True

        self.opened = False

        self.dismiss()

    def on_item_select(self, value):
        pass

    def select(self, widget):
        self.selected = widget
        self.dispatch("on_item_select", widget.text)

    def update_text(self, widget, value):
        if value.endswith("\n"):
            widget.text = value[:-1]
            self.apply_filter(value[:-1])
            children = self.drop_down.children[0].children
            if len(children) > 0:
                self.select(children[-1])
        else:
            self.apply_filter(value)

    def apply_filter(self, value):
        self.drop_down.clear_widgets()
        for btn in self.entries:
            match = True
            if value:
                for word in value.split(" "):
                    if word.lower() not in btn.lower():
                        match = False
            if match:
                button = self.button_factory(btn)
                button.bind(on_press=self.select)
                self.drop_down.add_widget(button)

    def open(self):
        self.apply_filter(self.input_area.text)
        self.drop_down.open(self.input_area)
        self.input_area.set_disabled(False)
        self.input_area.opacity = 1
        self.opened = True

    def dismiss(self):
        self.drop_down.dismiss()

    def real_dismiss(self, *args):
        self.input_area.set_disabled(True)
        self.input_area.opacity = 0
        self.opened = False

    def redraw(self, *args):
        super(FilterDD, self).redraw()

    def on_touch_down(self, touch):
        click = self.to_local(*touch.pos)
        if self.opened and not (self.input_area.collide_point(*click) or self.drop_down.collide_point(*click)):
            self.dismiss()

    def on_focus(self, *args):
        if not self.input_area.focused:
            self.dismiss()


class DrawerList(ThemableBehavior, MDList):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    """def set_color_item(self, instance_item):
        \"""Called when tap on a menu item.\"""

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color"""
