from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Инициализация SQLAlchemy
db = SQLAlchemy()


# Модель для таблицы task_statuses
class TaskStatus(db.Model):
    __tablename__ = 'task_statuses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    # Связь с таблицей tasks
    tasks = db.relationship('Task', backref='status', lazy=True)

    def __repr__(self):
        return f'<TaskStatus {self.name}>'

# Модель для таблицы tasks
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('task_statuses.id'), default=1)
    created_at = db.Column(db.DateTime, default="datetime.utcnow")

    # Связь с таблицей users (если она есть)
    user = db.relationship('User', backref='tasks')

    def __repr__(self):
        return f'<Task {self.title}>'

# Модель для таблицы users (если она есть)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Добавьте другие поля, если они есть в вашей таблице users
    
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<User {self.id}>'