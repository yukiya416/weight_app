from flask import Blueprint

reservation = Blueprint('reservation', __name__, url_prefix='/reservation',
                     template_folder='templates', static_folder='static')

from . import routes

# reservation_system/routes.py
from flask import render_template
from flask_login import login_required
from . import reservation

