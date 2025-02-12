from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модели

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Task(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)  # Используем db.Date для даты
    status = db.Column(db.String(20), default='Новая')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно. Теперь вы можете войти.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Вход выполнен успешно.')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.')

    return render_template('login.html')

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.')
    return redirect(url_for('login'))

# Добавление задачи
@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    try:
        # Получаем данные из формы
        title = request.form.get('title')
        description = request.form.get('description', '')  # Описание может быть пустым
        due_date_str = request.form.get('due_date')

        # Проверяем, что обязательные поля заполнены
        if not title or not due_date_str:
            flash('Заголовок и дата выполнения обязательны.', 'error')
            return redirect(url_for('index'))

        # Преобразуем строку даты в объект date
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Некорректный формат даты. Используйте формат ГГГГ-ММ-ДД.', 'error')
            return redirect(url_for('index'))

        # Создаем новую задачу
        new_task = Task(
            user_id=current_user.id,
            title=title,
            description=description,
            due_date=due_date
        )

        # Добавляем задачу в базу данных
        db.session.add(new_task)
        db.session.commit()

        flash('Задача успешно добавлена.', 'success')
    except Exception as e:
        # Откатываем изменения в случае ошибки
        db.session.rollback()
        flash('Произошла ошибка при добавлении задачи.', 'error')
        app.logger.error(f'Ошибка при добавлении задачи: {e}')

    return redirect(url_for('index'))

# Редактирование задачи
@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('У вас нет доступа к этой задаче.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        due_date_str = request.form['due_date']
        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        else:
            task.due_date = None
        db.session.commit()
        flash('Задача обновлена.')
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task)

# Удаление задачи
@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('У вас нет доступа к этой задаче.')
        return redirect(url_for('index'))

    db.session.delete(task)
    db.session.commit()
    flash('Задача удалена.')
    return redirect(url_for('index'))

# Главная страница
@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)