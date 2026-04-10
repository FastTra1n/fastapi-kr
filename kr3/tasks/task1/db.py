from models import User

USER_DATA = [
    User(**{"username": "admin", "password": "admin"})
]

def get_user_from_db(username: str):
    for user in USER_DATA:
        if user.username == username:
            return user
    return None