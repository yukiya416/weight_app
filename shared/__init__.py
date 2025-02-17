from flask import Blueprint

shared = Blueprint('shared', __name__, 
                  template_folder='templates',
                  static_folder='static')

from . import routes