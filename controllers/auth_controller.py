import bcrypt
from utils.db_helper import DatabaseHelper

class AuthController:
    def __init__(self):
        self.db = DatabaseHelper()

    def login(self, username, password):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                hashed_password = user["password_hash"].encode('utf-8') if isinstance(user["password_hash"], str) else user["password_hash"]
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True, user
            return False, None
        except Exception:
            return False, None
