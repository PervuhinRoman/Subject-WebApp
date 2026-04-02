import random
import re

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from faker import Faker

from userclass import User

fake = Faker()


app = Flask(__name__)
app.secret_key = 'mock'
app.config['SESSION_PERMANENT'] = False  # сессия сбрасывается при закрытии браузера
application = app


# Flask-Login настройка
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Список пользователей
users = {
    'user': User('1', 'user', generate_password_hash('qwerty')),
    'user1': User(2, 'user1', generate_password_hash('password'))
}


@login_manager.user_loader
def load_user(user_id):
    for username, user in users.items():
        if user.id == user_id:
            return user
    return None


# Редирект с flash-сообщением при попытке зайти без авторизации
@login_manager.unauthorized_handler
def unauthorized():
    flash('Для доступа к этой странице необходимо войти в систему.', 'danger')
    return redirect(url_for('login'))


images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']


def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = {'author': fake.name(), 'text': fake.text()}
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments


def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }


posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)


@app.route('/')
def index():
    session.permanent = False
    visits = session.get('visits', 0)
    session['visits'] = visits + 1

    welcome_msg = None
    if current_user.is_authenticated:
        welcome_msg = f"Добро пожаловать, {current_user.username}!"

    return render_template('index.html',
                           visits=visits + 1,
                           welcome_msg=welcome_msg)


@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)


@app.route('/posts/<int:index>')
def post(index):
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')


# Параметры URL
@app.route('/request-url')
def request_url():
    return render_template('request_url.html',
                           title='Параметры URL',
                           url_params=request.args)

# Заголовки
@app.route('/request-headers')
def request_headers():
    return render_template('request_headers.html',
                           title='Заголовки запроса',
                           headers=request.headers)

# Куки
@app.route('/request-cookies')
def request_cookies():
    return render_template('request_cookies.html',
                           title='Cookies',
                           cookies=request.cookies)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_data = {}  # Инициализируем пустой словарь для отображения данных формы

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form


        form_data = {
            'username': username,
            'password': generate_password_hash(password)  # Хешируем пароль для отображения
        }

        if username in users and check_password_hash(users[username].password_hash, password):
            login_user(users[username], remember=remember)
            flash('Успешный вход в систему!', 'success')
            return render_template('login.html', title='Вход', form_data=form_data)

        else:
            flash('Неверный логин или пароль!', 'danger')


    return render_template('login.html', title='Вход', form_data=form_data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


@app.route('/phone', methods=['GET', 'POST'])
def phone():
    phone_input = ''
    formatted = None
    error = None

    if request.method == 'POST':
        phone_input = request.form.get('phone', '')
        formatted, error = validate_phone(phone_input)

    return render_template('phone.html',
                           title='Проверка номера телефона',
                           phone_input=phone_input,
                           formatted=formatted,
                           error=error)


@app.route('/counter')
def counter():
    visits = session.get('counter_visits', 0)
    session['counter_visits'] = visits + 1
    return render_template('counter.html', title='Счётчик посещений', visits=visits + 1)


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html', title='Секретная страница')


def validate_phone(phone):
    if re.search(r'[^\d\s\(\)\-\.\+]', phone):
        return None, 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'

    digits = re.sub(r'[^0-9]', '', phone)
    stripped = phone.strip()
    if stripped.startswith('+7') or stripped.startswith('8'):
        required = 11
    else:
        required = 10

    if len(digits) != required:
        return None, 'Недопустимый ввод. Неверное количество цифр.'

    if len(digits) == 10:
        digits = '8' + digits

    formatted = f'8-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}'
    return formatted, None


if __name__ == '__main__':
    app.run(debug=True)
