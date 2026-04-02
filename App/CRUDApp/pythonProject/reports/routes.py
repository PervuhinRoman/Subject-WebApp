from flask import render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from . import reports_bp
from models import db, VisitLog, User
from decorators import check_rights
from .utils import generate_csv_by_page, generate_csv_by_user

PER_PAGE = 10


@reports_bp.route('/')
@login_required
def index():
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


@reports_bp.route('/by-page')
@check_rights('Администратор')
def by_page():
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


@reports_bp.route('/by-page/export')
@check_rights('Администратор')
def export_by_page():
    """Экспорт отчёта по страницам в CSV"""
    return generate_csv_by_page()


@reports_bp.route('/by-user')
@check_rights('Администратор')
def by_user():
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
            user = User.query.get(user_id)
            user_name = user.get_full_name() if user else 'Неизвестный пользователь'
        else:
            user_name = 'Неаутентифицированный пользователь'
        stats_with_names.append((user_name, count))

    return render_template(
        'reports/by_user.html',
        stats=stats_with_names,
        pagination=pagination
    )


@reports_bp.route('/by-user/export')
@check_rights('Администратор')
def export_by_user():
    """Экспорт отчёта по пользователям в CSV"""
    return generate_csv_by_user()