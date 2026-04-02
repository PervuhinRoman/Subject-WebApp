from flask import Blueprint

# Указываем путь к шаблонам относительно основного приложения
reports_bp = Blueprint('reports', __name__)

from . import routes