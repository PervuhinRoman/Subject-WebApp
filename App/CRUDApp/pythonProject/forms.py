from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length
from validators import validate_login, validate_password, validate_name


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Поле не может быть пустым')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле не может быть пустым')
    ])
    remember = StringField('Запомнить меня')
    submit = SubmitField('Войти')


class UserForm(FlaskForm):
    login = StringField('Логин', validators=[
        DataRequired(message='Поле не может быть пустым'),
        validate_login
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле не может быть пустым'),
        validate_password
    ])
    last_name = StringField('Фамилия')
    first_name = StringField('Имя', validators=[
        DataRequired(message='Поле не может быть пустым'),
        validate_name
    ])
    middle_name = StringField('Отчество')
    role_id = SelectField('Роль', coerce=int, validators=[
        DataRequired(message='Поле не может быть пустым')
    ])
    submit = SubmitField('Сохранить')


class EditUserForm(FlaskForm):
    last_name = StringField('Фамилия')
    first_name = StringField('Имя', validators=[
        DataRequired(message='Поле не может быть пустым'),
        validate_name
    ])
    middle_name = StringField('Отчество')
    role_id = SelectField('Роль', coerce=int, validators=[
        DataRequired(message='Поле не может быть пустым')
    ])
    submit = SubmitField('Сохранить')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[
        DataRequired(message='Поле не может быть пустым')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Поле не может быть пустым'),
        validate_password
    ])
    confirm_password = PasswordField('Повторите новый пароль', validators=[
        DataRequired(message='Поле не может быть пустым'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Изменить пароль')