import csv
from io import StringIO
from flask import make_response
from models import db, VisitLog, User


def generate_csv_by_page():
    """Генерация CSV отчёта по страницам"""
    # Получаем статистику посещений по страницам
    query = db.session.query(
        VisitLog.path,
        db.func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.path).order_by(db.desc('count')).all()

    # Создаём CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['№', 'Страница', 'Количество посещений'])

    for i, (path, count) in enumerate(query, 1):
        cw.writerow([i, path, count])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report_by_page.csv"
    output.headers["Content-type"] = "text/csv"
    return output


def generate_csv_by_user():
    """Генерация CSV отчёта по пользователям"""
    # Получаем статистику посещений по пользователям
    query = db.session.query(
        VisitLog.user_id,
        db.func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.user_id).order_by(db.desc('count')).all()

    # Создаём CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['№', 'Пользователь', 'Количество посещений'])

    for i, (user_id, count) in enumerate(query, 1):
        if user_id:
            user = User.query.get(user_id)
            user_name = user.get_full_name() if user else 'Неизвестный пользователь'
        else:
            user_name = 'Неаутентифицированный пользователь'

        cw.writerow([i, user_name, count])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report_by_user.csv"
    output.headers["Content-type"] = "text/csv"
    return output