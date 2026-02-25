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
    """Rectangle widget to represent a person on the canvas.
    An Escutcheon is a shield that forms the main or focal element in a coat of arms."""

    def __init__(self, hera_app, person, position=(20, 20), padding_x=30, padding_y=20, **kwargs):
        super().__init__(**kwargs)
        self.person = person  # store the person object
        self.hera_app = hera_app  # reference to the main app to call their methods
        self.position = position  # default position if not provided
        self.padding_x = padding_x  # horizontal padding for the rectangle
        self.padding_y = padding_y  # vertical padding for the rectangle
        self.label = None  # will hold the label graphics object
        self.rectangle = None  # will hold the rectangle graphics object
        self.outline = None  # will hold the outline graphics object

    def draw(self):
        self.draw_label()
        self.draw_rectangle()
        self.add_widget(self.label)

    def draw_label(self, font_size=12):
        """Draw the label with the person's data."""
        self.label = Label(
            text=f"{self.person.first_name} {self.person.last_name}\n* {self.person.date_of_birth}",
            size_hint=(None, None),
            font_size=font_size,
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1),
        )
        self.label.texture_update()  # update the texture to get the correct size
        self.label.size = self.label.texture_size  # set label size to fit the text
        self.label.pos = (  # position the label inside the rectangle (centered)
            self.position[0] + self.padding_x,
            self.position[1] + self.padding_y,
        )

    def draw_rectangle(self, padding_x=30, padding_y=20):
        rect_width = self.label.texture_size[0] + 2 * padding_x
        rect_height = self.label.texture_size[1] + 2 * padding_y
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rectangle = Rectangle(
                pos=self.position,
                size=(rect_width, rect_height),
            )
            Color(0, 0, 0, 1)
            self.outline = Line(rectangle=[*self.rectangle.pos, *self.rectangle.size], width=1)

    def on_touch_down(self, touch):
        """Handle touch events to open the popup for editing the person."""
        if self.collide_point(*touch.pos):
            print(f"Clicking Escutcheon for person={self.label.text} and id={self.person.id}")
            print(self.position)
            print(touch.pos)
            print(self.rectangle.size)
            self.hera_app.edit_person(self.person)


class Person:
    def __init__(self, hera_app, _id=None):
        self.hera_app = hera_app  # reference to the main app to call their methods
        self.content = GridLayout(cols=2, spacing=10, padding=10)  # layout for the popup
        self.popup = Popup(
            title="Add a new person",
            content=self.content,
            size_hint=(0.75, 0.5),
            auto_dismiss=True,
        )

        self._set_variables(_id)

    def _set_variables(self, _id):
        self.id = _id
        self.first_name = None
        self.last_name = None
        self.date_of_birth = None

    def open_popup(self, on_save):
        """Build popup with input fields and buttons."""
        self.content.clear_widgets()
        self.add_fields()

        # always set the fields, using existing self.person if present
        self.first_name_input.text = "" if self.first_name is None else self.first_name
        self.last_name_input.text = "" if self.last_name is None else self.last_name
        self.dob_input.text = "" if self.date_of_birth is None else self.date_of_birth

        self.add_buttons(on_save)
        self.popup.open()

    def add_fields(self):
        """Add input fields for the person's details"""
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

    def tab_key_navigation(self):
        """Alow tab key navigation in popup window."""
        self.first_name_input.next_input = self.last_name_input
        self.last_name_input.next_input = self.dob_input

    def add_buttons(self, on_save):
        save_button = Button(text="Save", size_hint=(0.5, 0.5))
        self.content.add_widget(save_button)
        save_button.bind(on_press=lambda instance: self.save_callback(on_save))

        test_button = Button(text="Test", size_hint=(0.5, 0.5))
        self.content.add_widget(test_button)
        test_button.bind(on_press=self.fill_test_data)

    def save_callback(self, on_save):
        self.parse_person_data()  # parse the input fields
        on_save(self)  # return save signal to main app
        self.popup.dismiss()  # close the popup after saving

    def parse_person_data(self):
        """Parse the input fields and call the save callback."""
        # get the input values
        first = self.first_name_input.text.strip()
        last = self.last_name_input.text.strip()
        dob = self.dob_input.text.strip()

        # check for data, return if no data
        if not first or not last or not dob:
            return

        # if not self.id:  # only generate a new ID if it doesn't exist
        #     self.id = str(uuid.uuid4())
        self.id = str(uuid.uuid4()) if self.id is None else self.id
        self.first_name = first
        self.last_name = last
        self.date_of_birth = dob

    def fill_test_data(self, instance):
        """Fill the input fields with random people data."""
        # get all people currently in the DB
        self.hera_app.db.cursor.execute("SELECT first_name, last_name FROM Person")
        existing = self.hera_app.db.cursor.fetchall()
        existing = set(" ".join(i) for i in existing)

        # fetch a random celebrity name and date of birth
        # from the existing names to avoid duplicates
        name, dob = random_celebrity(existing)

        if " " in name:
            first, last = name.split(" ", 1)
        else:
            first, last = name, ""

        self.first_name_input.text = first
        self.last_name_input.text = last
        self.dob_input.text = dob
