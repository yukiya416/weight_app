from flask import render_template
from flask_login import login_required
from . import reservation

@reservation.route('/')
@login_required
def index():
    """予約システム（準備中）"""
    return render_template('under_construction.html')