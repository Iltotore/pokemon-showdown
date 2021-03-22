from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.uix.button import Button
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList


class FDDButton(Button):
    pass


class FilterDD(Factory.DropDown, EventDispatcher):

    def __init__(self, buttons=(), **kwargs):
        super(FilterDD, self).__init__(**kwargs)
        self.register_event_type("on_item_select")
        self.entries = buttons
        self.input_area = Factory.TextInput(size_hint_y=None)
        self.selected = ""
        self.button_factory = lambda text: Factory.FDDButton(text=text)
        self.input_area.bind(text=self.update_text)
        self.multiline = False
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
            self.select(self.children[0].children[-2])
        else:
            self.apply_filter(value)

    def apply_filter(self, value):
        self.clear_widgets()
        self.add_widget(self.input_area)
        for btn in self.entries:
            match = True
            if value:
                for word in value.split(" "):
                    if word.lower() not in btn.lower():
                        match = False
            if match:
                button = self.button_factory(btn)
                button.bind(on_press=self.select)
                self.add_widget(button)

    def open(self, parent):
        self.apply_filter(self.input_area.text)
        super(FilterDD, self).open(parent)


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
