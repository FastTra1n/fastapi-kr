import secrets

from models import UserInDb

fake_users_db = {}

def get_user_from_db(username: str):
    for db_username, user in fake_users_db.items():
        if secrets.compare_digest(username, db_username):
            return user
    return None

def add_user_to_db(user: UserInDb):
    fake_users_db[user.username] = user