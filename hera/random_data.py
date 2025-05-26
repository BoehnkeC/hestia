import random

CELEBRITIES = [
    ("Albert Einstein", "1879-03-14"),
    ("Niels Bohr", "1885-10-07"),
    ("Mary Shelley", "1797-08-30"),
    ("Agatha Christie", "1890-09-15"),
    ("Ada Lovelace", "1815-12-10"),
    ("Isaac Newton", "1643-01-04"),
    ("Marie Curie", "1867-11-07"),
    ("Nikola Tesla", "1856-07-10"),
    ("Alan Turing", "1912-06-23"),
    ("Rosalind Franklin", "1920-07-25"),
    ("Leonardo da Vinci", "1452-04-15"),
    ("Charles Darwin", "1809-02-12"),
    ("Virginia Woolf", "1882-01-25"),
    ("Frida Kahlo", "1907-07-06"),
    ("Stephen Hawking", "1942-01-08"),
]


def random_celebrity(existing_people=None):
    """
    Return a random (first, last, dob) tuple not in existing_people.
    existing_people: set of (first, last) tuples.
    """
    if existing_people is None:
        existing_people = set()
    pool = [c for c in CELEBRITIES if c[0] not in existing_people]
    if not pool:
        return None, None
    return random.choice(pool)
