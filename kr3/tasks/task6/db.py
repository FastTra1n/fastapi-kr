import secrets

from models import User, Topic

fake_users_db = {}
fake_topics = {}

_topic_next_id = 1

def get_user_from_db(username: str):
    for db_username, user in fake_users_db.items():
        if secrets.compare_digest(username, db_username):
            return user
    return None

def add_user_to_db(user: User):
    fake_users_db[user.username] = user

def add_topic_to_db(topic: Topic):
    global _topic_next_id

    topic_id = _topic_next_id
    fake_topics[topic_id] = topic
    _topic_next_id += 1