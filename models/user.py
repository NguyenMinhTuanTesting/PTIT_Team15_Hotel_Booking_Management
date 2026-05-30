class User:
    def __init__(self, user_id=None, username=None, password_hash=None, role=None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
