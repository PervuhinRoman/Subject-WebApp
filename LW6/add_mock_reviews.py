from app.app import app
from app.models import db, Review, Course, User
from datetime import datetime, timedelta
import random

with app.app_context():
    COURSE_ID = 1
    USER_ID = 1

    course = db.session.get(Course, COURSE_ID)
    user = db.session.get(User, USER_ID)

    if not course or not user:
        print("❌ Ошибка: Курс или пользователь не найдены. Проверь ID в коде.")
        exit()

    texts = [
        "Отличный курс, очень доступно объясняют!",
        "Материал подан структурировано, но мало практики.",
        "Скучновато, много теории без примеров.",
        "Прекрасный преподаватель, всё по полочкам.",
        "Сложновато для старта, нужна база.",
        "Удобная платформа, задания проверяются быстро.",
        "Ожидал большего углубления в тему.",
        "Лучший курс по направлению!",
        "Домашки интересные и полезные.",
        "Материал немного устарел, но фундамент хороший."
    ]

    for t in texts:
        db.session.add(Review(
            course_id=course.id,
            user_id=user.id,
            rating=random.randint(1, 5),
            text=t,
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        ))

    db.session.commit()

    # Пересчёт рейтинга курса (требование ТЗ)
    all_reviews = db.session.execute(db.select(Review).filter_by(course_id=course.id)).scalars().all()
    course.rating_sum = sum(r.rating for r in all_reviews)
    course.rating_num = len(all_reviews)
    db.session.commit()

    print(f"✅ Добавлено {len(texts)} отзывов. Рейтинг курса: {course.rating:.2f}")