class Connection:
    def __init__(self):
        self.partner = None
        self.parents = None

    def find_parents(self):
        pass


class Person:
    def __init__(self, first_name=None, middle_name=None, last_name=None):
        self.gender = None
        self.title = None
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.birth_name = None  # the name the person had at birth, can change through marriage etc.
        self.nick_name = None  # the name the person is usually called with
        self.date_of_birth = None
        self.date_of_death = None
        self.date_of_marriage = None
        self.date_of_divorce = None
        self.connection = Connection()

    def living(self, date_of_birth=None, date_of_death=None):
        self.date_of_birth = date_of_birth
        self.date_of_death = date_of_death

    def marriage(self, date_of_marriage=None, date_of_divorce=None):
        self.date_of_marriage = date_of_marriage
        self.date_of_divorce = date_of_divorce
