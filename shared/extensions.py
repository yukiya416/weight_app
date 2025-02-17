from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def set_viewing_user_id(user_id):
    """セッションに表示中のユーザーIDを設定"""
    session['viewing_user_id'] = user_id

def get_viewing_user_id():
    """セッションから表示中のユーザーIDを取得"""
    return session.get('viewing_user_id')

def clear_viewing_user():
    """セッションから表示中のユーザー情報をクリア"""
    if 'viewing_user_id' in session:
        del session['viewing_user_id']