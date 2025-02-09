from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('savings_goal.id', ondelete="SET NULL"))
    goal = db.relationship("SavingsGoal", back_populates="users")
    contributions = db.relationship("Contribution", back_populates="user", lazy="dynamic")

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    users = db.relationship("User", back_populates="goal")

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="contributions")

class Item(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)  # Foreign key to Cart

    # Define a relationship to Cart
    cart = db.relationship('Cart', back_populates='items')  # Link back to Cart


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('Item', back_populates='cart', lazy='dynamic')  # Link back to Items

