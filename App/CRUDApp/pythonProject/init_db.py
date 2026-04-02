from models import db, User, Role, VisitLog
from werkzeug.security import generate_password_hash


def init_database(app):
    with app.app_context():
        # Создание таблиц
        db.create_all()

        # Создание ролей
        admin_role = Role.query.filter_by(name='Администратор').first()
        if not admin_role:
            admin_role = Role(name='Администратор', description='Полные права доступа')
            db.session.add(admin_role)

        user_role = Role.query.filter_by(name='Пользователь').first()
        if not user_role:
            user_role = Role(name='Пользователь', description='Обычный пользователь')
            db.session.add(user_role)

        db.session.commit()

        # Создание администратора
        admin = User.query.filter_by(login='admin').first()
        if not admin:
            admin = User(
                login='admin',
                last_name='Админов',
                first_name='Админ',
                middle_name='Админович',
                role_id=admin_role.id
            )
            admin.set_password('Admin123!')
            db.session.add(admin)

        # Создание обычного пользователя
        test_user = User.query.filter_by(login='user').first()
        if not test_user:
            test_user = User(
                login='user',
                last_name='Иванов',
                first_name='Иван',
                middle_name='Иванович',
                role_id=user_role.id
            )
            test_user.set_password('User123!')
            db.session.add(test_user)

        db.session.commit()
        print("База данных инициализирована успешно!")
        print("Логин администратора: admin, Пароль: Admin123!")
        print("Логин пользователя: user, Пароль: User123!")