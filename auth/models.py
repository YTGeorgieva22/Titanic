from __init__ import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    trainings = db.relationship("ModelTraining", backref="user", lazy=True)
    predictions = db.relationship("Prediction", backref="user", lazy=True)


class ModelTraining(db.Model):
    __tablename__ = 'ModelTraining'
    id = db.Column(db.Integer, primary_key=True)

    accuracy = db.Column(db.Float)
    epochs = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Prediction(db.Model):
    __tablename__ = 'Prediction'
    id = db.Column(db.Integer, primary_key=True)

    predicted_value = db.Column(db.Integer)   # 0 or 1
    actual_value = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))



