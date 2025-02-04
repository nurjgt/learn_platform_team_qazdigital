# test_units.py
import unittest
from main import cookie_generator, load_data, save_data
class TestUtils(unittest.TestCase):

    def test_cookie_generator(self):
        cookie = cookie_generator()
        self.assertEqual(len(cookie), 16)  # Cookie должен быть длиной 16 символов

    def test_load_save_data(self):
        test_data = {"users": [], "courses": [], "chapters": [], "cookies": []}
        save_data(test_data)
        loaded_data = load_data()
        self.assertEqual(loaded_data, test_data)

if __name__ == "__main__":
    unittest.main()