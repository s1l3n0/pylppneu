import unittest
from proplanguage import Atom


class PropLanguageTestCase(unittest.TestCase):

    def test_eq_atom(self):
        a1 = Atom("a")
        a2 = Atom("a")
        self.assertEqual(a1, a2)

if __name__ == '__main__':
    unittest.main()