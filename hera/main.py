import uuid

from kivy.app import App
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from hera.database import DB


class Calliope(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_input = None  # set this externally later

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "tab" and self.next_input:
            self.focus = False
            self.next_input.focus = True
            return True  # stop the event
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class PersonWidget(Widget):
    """Widget to represent a person on the canvas."""

    def __init__(self, name, dob, position, **kwargs):
        super().__init__(**kwargs)
        label_text = f"{name}\nDOB: {dob}"
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


class Hera(App):
    def build(self):
        self.db = DB()

        self.main_layout = BoxLayout(orientation="vertical")
        toolbar = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))

        self.add_buttons(toolbar)

        self.main_layout.add_widget(toolbar)  # add toolbar to the main layout

        # layout for displaying people
        self.canvas = FloatLayout()
        self.main_layout.add_widget(self.canvas)

        self.load_people_from_db()  # initial load of people from the database

        return self.main_layout

    def add_buttons(self, layout):
        add_person_button = Button(text="Add person")
        add_person_button.bind(on_press=self.open_add_person_popup)
        layout.add_widget(add_person_button)

    def open_add_person_popup(self, instance):
        content = GridLayout(cols=2, spacing=10, padding=10)  # layout for the popup

        # Input fields for the person's details
        content.add_widget(Label(text="First Name:"))
        first_name_input = Calliope(multiline=False)
        content.add_widget(first_name_input)

        content.add_widget(Label(text="Last Name:"))
        last_name_input = Calliope(multiline=False)
        content.add_widget(last_name_input)

        content.add_widget(Label(text="Date of Birth:"))
        dob_input = Calliope(multiline=False)
        content.add_widget(dob_input)

        # tab key navigation
        first_name_input.next_input = last_name_input
        last_name_input.next_input = dob_input

        # button to save the entry
        save_button = Button(text="Save", size_hint=(0.5, 0.5))

        # create the popup window
        popup = Popup(title="Add a new person", content=content, size_hint=(0.75, 0.5), auto_dismiss=True)

        save_button.bind(
            on_press=lambda x: self.save_person(first_name_input.text, last_name_input.text, dob_input.text, popup)
        )

        content.add_widget(save_button)

        popup.open()

    def save_person(self, first_name, last_name, date_of_birth, popup):
        person_id = str(uuid.uuid4())
        self.db.cursor.execute(  # insert the new person into the database
            """
            INSERT INTO Person (id, first_name, last_name, date_of_birth)
            VALUES (?, ?, ?, ?)
        """,
            (person_id, first_name, last_name, date_of_birth),
        )
        self.db.conn.commit()
        popup.dismiss()  # close the popup window
        self.refresh_canvas()  # refresh the canvas to add the new person

    def load_people_from_db(self):
        # fetch people data from the database
        self.db.cursor.execute("SELECT first_name, last_name, date_of_birth FROM Person")
        people = self.db.cursor.fetchall()

        # draw each person as a rectangle on the canvas
        y = 0.8  # starting y position for drawing rectangles
        self.canvas.clear_widgets()

        for person in people:
            name = f"{person[0]} {person[1]}"
            dob = person[2]
            position = (100, y * self.canvas.height)
            self.canvas.add_widget(PersonWidget(name=name, dob=dob, position=position))
            y -= 0.1  # decrement y position for each rectangle

    def refresh_canvas(self):
        self.load_people_from_db()  # reload the canvas with updated people data


if __name__ == "__main__":
    Hera().run()
