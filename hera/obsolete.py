"""
class Marriage(Node):
    def __init__(self, marriage_date):
        self.marriage_date = marriage_date
        self.divorced_date = None
        self.widowed_date = None

    def get_divorced(self, divorced_date):
        self.divorced_date = divorced_date

    def get_widowed(self, widowed_date):
        self.widowed_date = widowed_date


class Person:
    def __init__(self, first_name=None, middle_name=None, last_name=None):
        self.id = uuid.uuid1()
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
        self.node = None  # connect to another person

    def living_dates(self, date_of_birth=None, date_of_death=None):
        self.date_of_birth = date_of_birth
        self.date_of_death = date_of_death

    def marriage_dates(self, date_of_marriage=None, date_of_divorce=None):
        self.date_of_marriage = date_of_marriage
        self.date_of_divorce = date_of_divorce


class Node:
    def __init__(self, person_a, person_b):
        self.person_a = person_a
        self.person_b = person_b
        self.id = uuid.uuid1()
        self.ntype = None

    def get_type(self, event, _date):
        if event == "marriage":
            self.ntype = Marriage(marriage_date=_date)
"""
