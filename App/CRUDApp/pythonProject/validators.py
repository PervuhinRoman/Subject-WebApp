import re
from wtforms.validators import ValidationError


def validate_login(form, field):
    """Валидация логина: только латинские буквы и цифры, минимум 5 символов"""
    login = field.data

    if len(login) < 5:
        raise ValidationError('Логин должен содержать не менее 5 символов')

    if not re.match(r'^[a-zA-Z0-9]+$', login):
        raise ValidationError('Логин должен состоять только из латинских букв и цифр')


def validate_password(form, field):
    """Валидация пароля по требованиям задания"""
    password = field.data

    # Проверка длины
    if len(password) < 8:
        raise ValidationError('Пароль должен содержать не менее 8 символов')
    if len(password) > 128:
        raise ValidationError('Пароль должен содержать не более 128 символов')

    # Проверка на пробелы
    if ' ' in password:
        raise ValidationError('Пароль не должен содержать пробелы')

    # Проверка на наличие заглавной буквы
    if not re.search(r'[A-ZА-Я]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')

    # Проверка на наличие строчной буквы
    if not re.search(r'[a-zа-я]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')

    # Проверка на наличие цифры
    if not re.search(r'\d', password):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру')

    # Проверка на допустимые символы
    allowed_chars = r'^[a-zA-Zа-яА-Я0-9~!?@#$%^&*_\-+()[\]{}><\/\\|"\',.:;]+$'
    if not re.match(allowed_chars, password):
        raise ValidationError('Пароль содержит недопустимые символы')


def validate_name(form, field):
    """Валидация имени/фамилии: не может быть пустым"""
    if not field.data or not field.data.strip():
        raise ValidationError('Поле не может быть пустым')