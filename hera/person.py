import uuid

from kivy.graphics import Color, Line, Rectangle
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from hera.ancillary import Calliope
from hera.random_data import random_celebrity


class Escutcheon(Widget):
    """Widget to represent a person on the canvas.
    An Escutcheon is a shield that forms the main or focal element in a coat of arms."""

    def __init__(self, name, dob, position, person_id=None, hera_app=None, **kwargs):
        super().__init__(**kwargs)
        self.person_id = person_id
        self.hera_app = hera_app
        label_text = f"{name}\n* {dob}"
        self.label = Label(
            text=label_text,
            size_hint=(None, None),
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1),
        )
        # force the label to update its texture to get the correct size
        self.label.texture_update()
        label_width = self.label.texture_size[0]
        label_height = self.label.texture_size[1]

        # add padding to label
        padding_x = 30
        padding_y = 20
        rect_width = label_width + padding_x
        rect_height = label_height + padding_y

        # update label size and position
        self.label.size = (rect_width, rect_height)
        self.label.text_size = (rect_width, rect_height)
        self.label.pos = position

        with self.canvas:
            Color(1, 1, 1, 1)  # white fill
            self.rect = Rectangle(pos=position, size=(rect_width, rect_height))
            Color(0, 0, 0, 1)  # black edge
            self.outline = Line(rectangle=(position[0], position[1], rect_width, rect_height), width=1)

        self.add_widget(self.label)

    def on_touch_down(self, touch):
        """Handle touch events to edit the person when the rectangle is clicked."""
        if self.collide_point(*touch.pos):
            if self.hera_app and self.person_id:
                self.hera_app.edit_person(self.person_id)
            return True
        return super().on_touch_down(touch)


class Person:
    def __init__(self, hera_app, person=None):
        self.hera_app = hera_app  # reference to the main app to call their methods
        self.person = person  # for updating, otherwise None
        self.content = GridLayout(cols=2, spacing=10, padding=10)  # layout for the popup
        self.popup = Popup(
            title="Edit person" if person else "Add a new person",
            content=self.content,
            size_hint=(0.75, 0.5),
            auto_dismiss=True,
        )

        self.id: str | None = getattr(person, "id", None)
        self.first_name: str | None = getattr(person, "first_name", None)
        self.last_name: str | None = getattr(person, "last_name", None)
        self.date_of_birth: str | None = getattr(person, "date_of_birth", None)

    def save_callback(self, on_save):
        first = self.first_name_input.text.strip()
        last = self.last_name_input.text.strip()
        dob = self.dob_input.text.strip()
        if not first or not last or not dob:
            # Optionally show error
            return
        self.id = self.id or uuid.uuid4()
        self.first_name = first
        self.last_name = last
        self.date_of_birth = dob
        on_save(self)

    def open_popup(self, on_save):
        """Build popup with fields and buttons."""
        self.content.clear_widgets()
        self.add_fields()

        # Pre-fill fields if editing
        if self.person:
            self.first_name_input.text = self.person.first_name or ""
            self.last_name_input.text = self.person.last_name or ""
            self.dob_input.text = self.person.date_of_birth or ""

        self.add_buttons(on_save)
        self.popup.open()

    def add_fields(self):
        # input fields for the person's details
        self.content.add_widget(Label(text="First Name:"))
        self.first_name_input = Calliope(multiline=False)
        self.content.add_widget(self.first_name_input)

        self.content.add_widget(Label(text="Last Name:"))
        self.last_name_input = Calliope(multiline=False)
        self.content.add_widget(self.last_name_input)

        self.content.add_widget(Label(text="Date of Birth:"))
        self.dob_input = Calliope(multiline=False)
        self.content.add_widget(self.dob_input)

        self.tab_key_navigation()

    def add_person(self):
        self.id = str(uuid.uuid4())
        self.first_name = self.first_name_input.text
        self.last_name = self.last_name_input.text
        self.dob = self.dob_input.text

        if self.person:
            self.first_name_input.text = self.person.first_name
            self.last_name_input.text = self.person.last_name
            self.dob_input.text = self.person.date_of_birth

    def tab_key_navigation(self):
        # tab key navigation
        self.first_name_input.next_input = self.last_name_input
        self.last_name_input.next_input = self.dob_input

    def add_buttons(self, on_save):
        save_button = Button(text="Update" if self.person else "Save", size_hint=(0.5, 0.5))
        save_button.bind(on_press=lambda instance: self.save_callback(on_save))

        test_button = Button(text="Test", size_hint=(0.5, 0.5))
        test_button.bind(on_press=self.fill_test_data)

        self.content.add_widget(save_button)
        self.content.add_widget(test_button, index=0)  # insert Test button at the top left (row 0, col 0)

    def fill_test_data(self, instance):
        # get all people currently in the DB
        self.hera_app.db.cursor.execute("SELECT first_name, last_name FROM Person")
        existing = self.hera_app.db.cursor.fetchall()
        existing = set(" ".join(i) for i in existing)

        name, dob = random_celebrity(existing)

        if " " in name:
            first, last = name.split(" ", 1)
        else:
            first, last = name, ""
        self.first_name_input.text = first
        self.last_name_input.text = last
        self.dob_input.text = dob

        self.add_person()  # update the person data with the test values
