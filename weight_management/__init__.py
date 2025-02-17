from flask import Blueprint

weight = Blueprint('weight', __name__, 
                  template_folder='templates',
                  static_folder='static')

from . import routes