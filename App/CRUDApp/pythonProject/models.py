from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(100))
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        parts = []
        if self.last_name:
            parts.append(self.last_name)
        parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

    def has_role(self, role_name):
        """Проверка наличия роли у пользователя"""
        return self.role and self.role.name == role_name

    def __repr__(self):
        return f'<User {self.login}>'


class VisitLog(db.Model):
    __tablename__ = 'visit_logs'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='visits')

    def __repr__(self):
        return f'<VisitLog {self.path} by {self.user_id}>'