from fastapi import FastAPI

from models import User, FeedBack

app = FastAPI()

users = []
reviews = []

def is_adult(age):
    return age >= 18

def response_review(author):
    return f"Feedback received. Thank you, {author}."

@app.get('/users')
async def get_users():
    return users

@app.get('/reviews')
async def get_reviews():
    return reviews

@app.post('/user')
async def create_user(user: User):
    new_user = {"name": user.name, "age": user.age, "is_adult": is_adult(user.age)}
    users.append(new_user)
    return new_user

@app.post('/feedback')
async def leave_review(feedback: FeedBack):
    reviews.append(feedback)
    return response_review(feedback.name)