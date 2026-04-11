import sys
from app.app import app
from app.models import db, User

NEW_USER = {
    "first_name": "Федя",
    "last_name": "Петров",
    "middle_name": "Петрович",
    "login": "user2",
    "password": "qwerty"
}

with app.app_context():
    login = NEW_USER["login"]

    # 1. Проверка на существование
    existing = db.session.execute(
        db.select(User).filter_by(login=login)
    ).scalar_one_or_none()

    if existing:
        print(f"⚠️  Пользователь с логином '{login}' уже существует (ID: {existing.id})")
        sys.exit(0)

    # 2. Создание объекта
    user = User(
        first_name=NEW_USER["first_name"],
        last_name=NEW_USER["last_name"],
        middle_name=NEW_USER["middle_name"],
        login=NEW_USER["login"]
    )
    user.set_password(NEW_USER["password"])

    # 3. Сохранение с обработкой ошибок
    db.session.add(user)
    try:
        db.session.commit()
        print("✅ Пользователь успешно добавлен в БД!")
        print(f"👤 {user.last_name} {user.first_name} ({user.middle_name or ''})")
        print(f"🔑 Логин: {user.login}")
        print(f"🆔 ID: {user.id}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при сохранении: {e}")
        sys.exit(1)