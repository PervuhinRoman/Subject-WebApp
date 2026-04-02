import os
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Role, VisitLog
from forms import LoginForm, UserForm, EditUserForm, ChangePasswordForm
from init_db import init_database
from decorators import check_rights
from reports import reports_bp
from reports.utils import generate_csv_by_page, generate_csv_by_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False

# Регистрация Blueprint для отчётов
app.register_blueprint(reports_bp, url_prefix='/reports')

# Инициализация расширений
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# User loader для Flask-Login (исправлено для SQLAlchemy 2.0+)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Обработчик неавторизованного доступа
@login_manager.unauthorized_handler
def unauthorized():
    flash('Для доступа к этой странице необходимо войти в систему.', 'danger')
    return redirect(url_for('login'))


# Before request - логирование посещений
@app.before_request
def log_visit():
    # Исключаем запросы к статическим файлам и самим логам
    excluded_paths = ['/static/', '/reports/', '/login', '/logout', '/favicon.ico']

    if request.path.startswith(tuple(excluded_paths)):
        return

    # Проверяем, что это не повторный вызов (защита от рекурсии)
    if not hasattr(g, 'visit_logged'):
        g.visit_logged = True

        # Создаём запись в журнале
        visit = VisitLog(
            path=request.path,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(visit)
        try:
            db.session.commit()
        except:
            db.session.rollback()


# Главная страница - список пользователей
@app.route('/')
def index():
    users = User.query.order_by(User.id).all()
    return render_template('index.html', users=users)


# === МАРШРУТЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ===

@app.route('/users/create', methods=['GET', 'POST'])
@check_rights('Администратор')
def user_create():
    form = UserForm()

    # Заполнение списка ролей
    roles = Role.query.all()
    form.role_id.choices = [(role.id, role.name) for role in roles]

    if form.validate_on_submit():
        try:
            # Проверка уникальности логина
            existing_user = User.query.filter_by(login=form.login.data).first()
            if existing_user:
                flash('Пользователь с таким логином уже существует!', 'danger')
                return render_template('user_form.html', form=form, title='Создание пользователя', mode='create')

            # Создание нового пользователя
            user = User(
                login=form.login.data,
                last_name=form.last_name.data.strip() if form.last_name.data else None,
                first_name=form.first_name.data.strip(),
                middle_name=form.middle_name.data.strip() if form.middle_name.data else None,
                role_id=form.role_id.data
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash('Пользователь успешно создан!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании пользователя: {str(e)}', 'danger')

    return render_template('user_form.html', form=form, title='Создание пользователя', mode='create')


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash('Пользователь не найден!', 'danger')
        return redirect(url_for('index'))

    # Проверка прав
    if not current_user.has_role('Администратор'):
        if user.id != current_user.id:
            flash('У вас недостаточно прав для редактирования этого пользователя.', 'danger')
            return redirect(url_for('index'))

    form = EditUserForm()

    # Заполнение списка ролей
    roles = Role.query.all()

    # Для обычного пользователя поле роли отключено
    if current_user.has_role('Администратор'):
        form.role_id.choices = [(role.id, role.name) for role in roles]
    else:
        form.role_id.choices = [(user.role_id, user.role.name if user.role else '')]
        form.role_id.render_kw = {'disabled': 'disabled'}

    if request.method == 'GET':
        # Заполнение формы текущими данными
        form.last_name.data = user.last_name
        form.first_name.data = user.first_name
        form.middle_name.data = user.middle_name
        form.role_id.data = user.role_id

    if form.validate_on_submit():
        try:
            user.last_name = form.last_name.data.strip() if form.last_name.data else None
            user.first_name = form.first_name.data.strip()
            user.middle_name = form.middle_name.data.strip() if form.middle_name.data else None

            # Роль можно изменить только администратору
            if current_user.has_role('Администратор'):
                user.role_id = form.role_id.data

            db.session.commit()
            flash('Данные пользователя успешно обновлены!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении данных: {str(e)}', 'danger')

    return render_template('user_form.html', form=form, title='Редактирование пользователя', mode='edit',
                           user_id=user_id)


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@check_rights('Администратор')
def user_delete(user_id):
    if user_id == current_user.id:
        flash('Нельзя удалить самого себя!', 'danger')
        return redirect(url_for('index'))

    user = db.session.get(User, user_id)
    if user is None:
        flash('Пользователь не найден!', 'danger')
        return redirect(url_for('index'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удалён!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')

    return redirect(url_for('index'))


@app.route('/users/<int:user_id>')
@login_required
def user_view(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash('Пользователь не найден!', 'danger')
        return redirect(url_for('index'))

    # Проверка прав: администратор видит всех, пользователь - только себя
    if not current_user.has_role('Администратор'):
        if user.id != current_user.id:
            flash('У вас недостаточно прав для просмотра этого профиля.', 'danger')
            return redirect(url_for('index'))

    return render_template('user_view.html', user=user)


# === АУТЕНТИФИКАЦИЯ ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(login=username).first()

        if user and user.check_password(password):
            login_user(user, remember=bool(form.remember.data))
            flash('Успешный вход в систему!', 'success')

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


# === ИЗМЕНЕНИЕ ПАРОЛЯ ===

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        try:
            # Проверка старого пароля
            if not current_user.check_password(form.old_password.data):
                flash('Неверный старый пароль!', 'danger')
                return render_template('change_password.html', form=form)

            # Обновление пароля
            current_user.set_password(form.new_password.data)
            db.session.commit()

            flash('Пароль успешно изменён!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при изменении пароля: {str(e)}', 'danger')

    return render_template('change_password.html', form=form)


# === ОТЧЁТЫ ===

PER_PAGE = 10


@app.route('/reports/')
@login_required
def reports_index():
    """Главная страница журнала посещений"""

    # Проверка прав: администратор видит все, пользователь - только свои
    if current_user.has_role('Администратор'):
        query = VisitLog.query
    else:
        query = VisitLog.query.filter_by(user_id=current_user.id)

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(VisitLog.created_at.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False
    )
    visits = pagination.items

    return render_template(
        'reports/index.html',
        visits=visits,
        pagination=pagination
    )


@app.route('/reports/by-page')
@check_rights('Администратор')
def reports_by_page():
    """Отчёт по страницам"""
    page = request.args.get('page', 1, type=int)

    # Получаем статистику посещений по страницам
    query = db.session.query(
        VisitLog.path,
        db.func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.path).order_by(db.desc('count'))

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    stats = pagination.items

    return render_template(
        'reports/by_page.html',
        stats=stats,
        pagination=pagination
    )


@app.route('/reports/by-page/export')
@check_rights('Администратор')
def reports_export_by_page():
    """Экспорт отчёта по страницам в CSV"""
    return generate_csv_by_page()


@app.route('/reports/by-user')
@check_rights('Администратор')
def reports_by_user():
    """Отчёт по пользователям"""
    page = request.args.get('page', 1, type=int)

    # Получаем статистику посещений по пользователям
    query = db.session.query(
        VisitLog.user_id,
        db.func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.user_id).order_by(db.desc('count'))

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    stats = pagination.items

    # Получаем полные имена пользователей
    stats_with_names = []
    for user_id, count in stats:
        if user_id:
            user = db.session.get(User, user_id)
            user_name = user.get_full_name() if user else 'Неизвестный пользователь'
        else:
            user_name = 'Неаутентифицированный пользователь'
        stats_with_names.append((user_name, count))

    return render_template(
        'reports/by_user.html',
        stats=stats_with_names,
        pagination=pagination
    )


@app.route('/reports/by-user/export')
@check_rights('Администратор')
def reports_export_by_user():
    """Экспорт отчёта по пользователям в CSV"""
    return generate_csv_by_user()


if __name__ == '__main__':
    with app.app_context():
        # Инициализация базы данных при первом запуске
        if not os.path.exists('users.db'):
            init_database(app)

    app.run(debug=True)