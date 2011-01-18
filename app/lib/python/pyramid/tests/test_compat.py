import unittest

class TestAliases(unittest.TestCase):
    def test_all(self):
        from pyramid.compat import all
        self.assertEqual(all([True, True]), True)
        self.assertEqual(all([False, False]), False)
        self.assertEqual(all([False, True]), False)

