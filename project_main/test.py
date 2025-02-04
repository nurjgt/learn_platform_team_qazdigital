import unittest
import hashlib
from main import hash_password, cookie_generator, get_user_by_cookie, load_data, save_data

class TestHashPassword(unittest.TestCase):
    def test_hash_password_correctness(self):
        password = "securepassword"
        expected_hash = hashlib.sha1(password.encode("utf-8")).hexdigest()
        self.assertEqual(hash_password(password), expected_hash, "Hash does not match expected value")

class TestCookieGenerator(unittest.TestCase):
    def test_cookie_length(self):
        cookie = cookie_generator()
        self.assertEqual(len(cookie), 16, "Cookie length should be 16")

    def test_cookie_alphanumeric(self):
        cookie = cookie_generator()
        self.assertTrue(cookie.isalnum(), "Cookie should be alphanumeric")

class TestGetUserByCookie(unittest.TestCase):
    def setUp(self):
        # Prepare test data
        self.data = load_data()
        self.user = {"id": "1", "username": "testuser"}
        self.cookie = "testcookie123456"
        self.data["users"].append(self.user)
        self.data["cookies"].append({"cookie": self.cookie, "user_id": self.user["id"]})
        save_data(self.data)

    def tearDown(self):
        # Clean up test data
        self.data["users"].remove(self.user)
        self.data["cookies"] = [c for c in self.data["cookies"] if c["cookie"] != self.cookie]
        save_data(self.data)

    def test_get_existing_user_by_cookie(self):
        result = get_user_by_cookie(self.cookie)
        self.assertIsNotNone(result, "User should not be None")
        self.assertEqual(result["username"], "testuser", "Usernames should match")

    def test_get_nonexistent_user_by_cookie(self):
        result = get_user_by_cookie("invalidcookie")
        self.assertIsNone(result, "User should be None for invalid cookie")

if __name__ == "__main__":
    unittest.main()
