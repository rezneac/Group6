import os
from app import bcrypt
from werkzeug.security import generate_password_hash
from models import db, User, SavingsGoal, Contribution
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'super_secret_key'  # Change this in production!
db.init_app(app)

def create_database():
    with app.app_context():
        db.create_all()

        # Insert savings goals
        goals = [
            SavingsGoal(id=1, name="Holiday Fund", target_amount=1000.00),
            SavingsGoal(id=2, name="New Car Fund", target_amount=5000.00)
        ]
        db.session.bulk_save_objects(goals)
        db.session.commit()

        # Test users with hashed passwords, linked to different goals
        users = [
            User(username="john_doe", email="john@example.com", password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'), goal_id=1),
            User(username="jane_smith", email="jane@example.com", password_hash=bcrypt.generate_password_hash("securepass").decode('utf-8'), goal_id=1),
            User(username="alice_wonder", email="alice@example.com", password_hash=bcrypt.generate_password_hash("alice123").decode('utf-8'), goal_id=2)
        ]
        db.session.bulk_save_objects(users)
        db.session.commit()

        # Get user IDs
        user_ids = {user.username: user.id for user in User.query.all()}

        # Test contributions
        contributions = [
            Contribution(user_id=user_ids["john_doe"], amount=100, date=datetime(2025, 2, 8)),
            Contribution(user_id=user_ids["jane_smith"], amount=200, date=datetime(2025, 2, 8)),
            Contribution(user_id=user_ids["alice_wonder"], amount=150, date=datetime(2025, 2, 7)),
            Contribution(user_id=user_ids["john_doe"], amount=50, date=datetime(2025, 2, 7))
        ]
        db.session.bulk_save_objects(contributions)
        db.session.commit()

        print("Database created successfully with test users, shared goals, and contributions.")

if __name__ == "__main__":
    create_database()