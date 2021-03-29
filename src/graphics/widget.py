from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList


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
        self.input_area.unfocus_on_touch = True
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
            self.select(self.drop_down.children[0].children[-1])
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
        print("dismiss")
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
