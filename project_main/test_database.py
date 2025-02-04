import unittest
import json
import sys
sys.path.insert(0, ".")  # Добавляет текущую папку в путь импорта
from main import app


class TestSecurity(unittest.TestCase):
    def setUp(self):
        """Настраиваем тестовый клиент"""
        self.app = app.test_client()
        self.app.testing = True

    def test_sql_injection_login(self):
        """Попытка входа с SQL-инъекцией"""
        payload = {
            "username": "' OR '1'='1",
            "password": "password"
        }
        response = self.app.post("/login", data=payload)

        # Проверяем, что не пускает в систему
        self.assertNotIn("Set-Cookie", response.headers)
        self.assertIn(b"Invalid login", response.data)

if __name__ == "__main__":
    unittest.main()
