from statistics import mean

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from hera.database import DB
from hera.person import Escutcheon, Person


class Hera(App):
    def build(self):
        self.db = DB()
        self.escutcheons = {}  # track all escutcheons

        self.main_layout = BoxLayout(orientation="vertical")
        self.toolbar = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        self.add_buttons()
        self.main_layout.add_widget(self.toolbar)  # add toolbar to the main layout

        # layout for displaying people
        self.canvas = FloatLayout()
        self.main_layout.add_widget(self.canvas)

        # bind to size changes so we always have up-to-date sizes
        self.canvas.bind(size=self.on_layout_size)
        self.toolbar.bind(size=self.on_layout_size)

        self.load_people_from_db()  # initial load of people from the database

        return self.main_layout

    def on_layout_size(self, *args):
        # dummy handler to force recalculation if needed
        pass

    def add_buttons(self):
        """Add buttons to the toolbar."""
        add_person_button = Button(text="Add person")
        self.toolbar.add_widget(add_person_button)
        add_person_button.bind(on_press=self.open_add_person_popup)

    def open_add_person_popup(self, instance):
        """Open the popup to add a new person or edit an existing one."""
        person = Person(self)
        person.open_popup(on_save=lambda p: self.save_person(p, edit=False))  # save callback to popup

    def edit_person(self, person):
        person.open_popup(on_save=lambda p: self.save_person(p, edit=True))

    def save_person(self, person, edit=False):
        """Callback to save the person data."""
        if edit:
            escutcheon = self.escutcheons.get(person.id)
            self.canvas.remove_widget(escutcheon)
            self.person_to_canvas(person, escutcheon)

        else:
            self.person_to_canvas(person)

        self.save_person_to_db(person)
        self.arrange_escutcheons()
        self.save_escutcheons_to_db()

    def save_person_to_db(self, person):
        """Save the person to the database."""
        self.db.cursor.execute(
            "INSERT OR REPLACE INTO Person (id, first_name, last_name, date_of_birth) VALUES (?, ?, ?, ?)",
            (
                person.id,
                person.first_name,
                person.last_name,
                person.date_of_birth,
            ),
        )
        self.db.conn.commit()

    def person_to_canvas(self, person, escutcheon=None):
        """Add the person to the canvas."""
        if escutcheon is None:
            escutcheon = Escutcheon(
                self,
                person,
            )

        escutcheon.draw()
        self.canvas.add_widget(escutcheon)
        self.escutcheons[person.id] = escutcheon
        # Optionally, you can also store the escutcheon in a list or dictionary for later reference
        # self.escutcheons.append(escutcheon)

    def arrange_escutcheons(self):
        esc_width = mean([esc.rectangle.size[0] for esc in self.escutcheons.values()])
        esc_height = mean([esc.rectangle.size[1] for esc in self.escutcheons.values()])
        spacing = (
            (self.canvas.width - len(self.escutcheons) * esc_width) / (len(self.escutcheons) + 1)
            if len(self.escutcheons) > 0
            else 0
        )

        for i, esc in enumerate(self.escutcheons.values()):
            x = spacing + i * (esc_width + spacing)
            y = (self.canvas.height - esc_height) / 2  # Center vertically
            esc.rectangle.pos = (x, y)
            esc.label.pos = (  # position the label inside the rectangle (centered)
                esc.rectangle.pos[0] + esc.padding_x,
                esc.rectangle.pos[1] + esc.padding_y,
            )

    def save_escutcheons_to_db(self):
        """Save all escutcheons to the database."""
        for esc in self.escutcheons.values():
            self.db.cursor.execute(
                "INSERT OR REPLACE INTO Escutcheons (id, x, y, width, height) VALUES (?, ?, ?, ?, ?)",
                (
                    esc.person.id,
                    esc.rectangle.pos[0],
                    esc.rectangle.pos[1],
                    esc.rectangle.size[0],
                    esc.rectangle.size[1],
                ),
            )
        self.db.conn.commit()

    def load_people_from_db(self):
        """Load all people from the database and display them."""
        self.db.cursor.execute("SELECT id, first_name, last_name, date_of_birth FROM Person")
        persons = self.db.cursor.fetchall()
        escutcheons = self.db.get_escutcheons()

        if len(persons) == 0 and len(escutcheons) == 0:
            return

        for p, esc in zip(persons, escutcheons, strict=True):
            person_id, first, last, dob = p
            person = Person(self)
            person.id = person_id
            person.first_name = first
            person.last_name = last
            person.date_of_birth = dob

            _, x, y, _, _ = esc
            escutcheon = Escutcheon(
                self,
                person,
                position=(x, y),
            )
            self.person_to_canvas(person, escutcheon)


if __name__ == "__main__":
    Hera().run()
