from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


# Добавили UserMixin в скобки!
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)  # Уникальный логин
    password = db.Column(db.String(200), nullable=False)  # Хэш пароля
    name = db.Column(db.String(100), nullable=False)  # Имя
    status = db.Column(db.String(50), default="Студент")
    points = db.Column(db.Integer, default=0)

    participations = db.relationship('Participation', backref='user', lazy=True)


class Participation(db.Model):
    __tablename__ = 'participations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    event_title = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)