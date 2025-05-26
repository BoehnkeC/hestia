from kivy.uix.textinput import TextInput


class Calliope(TextInput):
    """A TextInput that allows navigation to the next input field using the Tab key."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_input = None  # set this externally later

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "tab" and self.next_input:
            self.focus = False
            self.next_input.focus = True
            return True  # stop the event
        return super().keyboard_on_key_down(window, keycode, text, modifiers)
