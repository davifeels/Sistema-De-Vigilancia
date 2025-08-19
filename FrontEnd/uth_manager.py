# auth_manager.py
import json
import bcrypt

class AuthManager:
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.users = self._load_users()

    def _load_users(self):
        try:
            with open(self.users_file, "r") as f:
                data = json.load(f)
                return data.get("users", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def authenticate(self, username, password):
        for user in self.users:
            if user['username'] == username:
                # Verifica a senha com o hash armazenado
                if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    return user
        return None

    def get_role(self, username):
        for user in self.users:
            if user['username'] == username:
                return user['role']
        return None