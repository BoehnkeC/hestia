import unittest

from src.main import Node, Person


class Prepare(unittest.TestCase):
    def test_create_person(self):
        person_a = Person(first_name="Friedrich", middle_name="Wilhelm", last_name="von Humboldt")
        person_a.gender = "male"
        person_a.nick_name = "Wilhelm"

        self.assertEqual(person_a.first_name, "Friedrich")
        self.assertEqual(person_a.middle_name, "Wilhelm")
        self.assertEqual(person_a.last_name, "von Humboldt")
        self.assertEqual(person_a.nick_name, "Wilhelm")
        self.assertEqual(person_a.gender, "male")

    def test_unique_persons(self):
        """Test unique person IDs as two persons may have the same name."""

        person_a = Person(first_name="Friedrich", middle_name="Wilhelm", last_name="von Humboldt")

        person_b = Person(first_name="Friedrich", middle_name="Wilhelm", last_name="von Humboldt")

        self.assertNotEqual(person_a.id, person_b.id)

    def test_node(self):
        """Test if node connects people correctly."""
        person_a = Person(first_name="Friedrich", last_name="von Humboldt")
        person_b = Person(first_name="Caroline", last_name="von Humboldt")

        node = Node(person_a=person_a, person_b=person_b)
        node.get_type(event="marriage", _date="2021-07-31")
        print(node.ntype)

    def test_children(self):
        parent_a = Person(first_name="Friedrich", middle_name="Wilhelm", last_name="von Humboldt")
        parent_b = Person(first_name="Caroline", last_name="von Humboldt")

        child_a = Person(first_name="Gabriele", last_name="von Bülow")

        connection = child_a.connection
        connection.partner = person_b


if __name__ == "__main__":
    unittest.main()
