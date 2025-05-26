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
from hera.random_data import random_celebrity


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


class PersonMask:
    def __init__(self, hera_app, person=None):
        self.hera_app = hera_app  # reference to the main app to call their methods
        self.person = person  # person data as dict or None
        self.content = GridLayout(cols=2, spacing=10, padding=10)  # layout for the popup
        self.popup = Popup(
            title="Edit person" if person else "Add a new person",
            content=self.content,
            size_hint=(0.75, 0.5),
            auto_dismiss=True,
        )

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

        if self.person:
            self.first_name_input.text = self.person["first_name"]
            self.last_name_input.text = self.person["last_name"]
            self.dob_input.text = self.person["date_of_birth"]

        self.tab_key_navigation()

    def tab_key_navigation(self):
        # tab key navigation
        self.first_name_input.next_input = self.last_name_input
        self.last_name_input.next_input = self.dob_input

    def add_buttons(self):
        if self.person:
            save_button = Button(text="Update", size_hint=(0.5, 0.5))
            save_button.bind(
                on_press=lambda x: self.hera_app.update_person(
                    self.person["id"],
                    self.first_name_input.text,
                    self.last_name_input.text,
                    self.dob_input.text,
                    self.popup,
                )
            )
        else:
            save_button = Button(text="Save", size_hint=(0.5, 0.5))
            save_button.bind(
                on_press=lambda x: self.hera_app.save_person(
                    self.first_name_input.text, self.last_name_input.text, self.dob_input.text, self.popup
                )
            )

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
        person_mask = PersonMask(self)
        person_mask.add_fields()  # add input fields to the popup
        person_mask.add_buttons()  # add buttons to the popup
        person_mask.popup.open()

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
        self.db.cursor.execute("SELECT id, first_name, last_name, date_of_birth FROM Person")
        people = self.db.cursor.fetchall()

        # draw each person as a rectangle on the canvas
        y = 0.8  # starting y position for drawing rectangles
        self.canvas.clear_widgets()

        for person in people:
            person_id, first_name, last_name, dob = person
            name = f"{first_name} {last_name}"
            position = (100, y * self.canvas.height)
            self.canvas.add_widget(
                Escutcheon(
                    name=name,
                    dob=dob,
                    position=position,
                    person_id=person_id,
                    hera_app=self,
                )
            )
            y -= 0.1  # decrement y position for each rectangle

    def edit_person(self, person_id):
        # fetch person data by id
        self.db.cursor.execute(
            "SELECT id, first_name, last_name, date_of_birth FROM Person WHERE id = ?", (person_id,)
        )
        row = self.db.cursor.fetchone()
        if row:
            person = {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "date_of_birth": row[3],
            }
            person_mask = PersonMask(self, person=person)
            person_mask.add_fields()
            person_mask.add_buttons()
            person_mask.popup.open()

    def update_person(self, person_id, first_name, last_name, date_of_birth, popup):
        self.db.cursor.execute(
            """
            UPDATE Person
            SET first_name = ?, last_name = ?, date_of_birth = ?
            WHERE id = ?
            """,
            (first_name, last_name, date_of_birth, person_id),
        )
        self.db.conn.commit()
        popup.dismiss()
        self.refresh_canvas()

    def refresh_canvas(self):
        self.load_people_from_db()  # reload the canvas with updated people data


if __name__ == "__main__":
    Hera().run()
