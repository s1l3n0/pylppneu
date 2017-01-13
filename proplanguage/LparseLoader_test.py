import unittest
from LparseLoader import parseString

class PropLanguageTestCase(unittest.TestCase):

    def test_parsing1(self):
        parseString("b :- a.")

if __name__ == '__main__':
    unittest.main()