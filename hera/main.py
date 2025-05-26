from collections import namedtuple

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from hera.database import DB
from hera.person import Escutcheon, Person


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
        person = Person(self)
        person.open_popup(on_save=self.save_person)

    def save_person(self, person):
        self.db.cursor.execute(  # insert the new person into the database
            """
            INSERT INTO Person (id, first_name, last_name, date_of_birth)
            VALUES (?, ?, ?, ?)
        """,
            (person.id, person.first_name, person.last_name, person.date_of_birth),
        )
        self.db.conn.commit()
        person.popup.dismiss()  # close the popup window
        self.refresh_canvas()  # refresh the canvas to add the new person

    def load_people_from_db(self):
        # fetch people data from the database
        self.db.cursor.execute("SELECT id, first_name, last_name, date_of_birth FROM Person")
        people = self.db.cursor.fetchall()

        # draw each person as a rectangle on the canvas
        y = 0.8  # starting y position for drawing rectangles
        self.canvas.clear_widgets()

        for p in people:
            person_id, first_name, last_name, dob = p
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
            PersonTuple = namedtuple("PersonTuple", ["id", "first_name", "last_name", "date_of_birth"])
            person_obj = PersonTuple(
                id=row[0],
                first_name=row[1],
                last_name=row[2],
                date_of_birth=row[3],
            )
            person = Person(self, person=person_obj)
            person.open_popup(on_save=self.update_person)

    def update_person(self, person):
        self.db.cursor.execute(
            """
            UPDATE Person
            SET first_name = ?, last_name = ?, date_of_birth = ?
            WHERE id = ?
            """,
            (person.first_name, person.last_name, person.date_of_birth, person.id),
        )
        self.db.conn.commit()
        person.popup.dismiss()
        self.refresh_canvas()

    def refresh_canvas(self):
        self.load_people_from_db()  # reload the canvas with updated people data


if __name__ == "__main__":
    Hera().run()
