from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def check_rights(required_role):
    """
    Декоратор для проверки прав пользователя

    :param required_role: требуемая роль ('Администратор' или 'Пользователь')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для доступа к данной странице необходимо войти в систему.', 'danger')
                return redirect(url_for('login'))

            if not current_user.has_role(required_role):
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('index'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator