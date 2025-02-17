from datetime import timedelta
import os

from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from shared.extensions import db, login_manager
from shared.models.user import User



# プロジェクトのルートディレクトリを取得
basedir = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    
    # アプリケーション設定
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "instance", "app.db")}').replace('postgres://', 'postgresql://'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PERMANENT_SESSION_LIFETIME=timedelta(days=365 * 10),  # 10年間
        SESSION_PERMANENT=True,
        WTF_CSRF_ENABLED=True  # CSRF保護を有効化
    )

    # CSRFの初期化
    csrf = CSRFProtect()
    csrf.init_app(app)

    # instanceフォルダの作成
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

    # 拡張機能の初期化
    init_extensions(app)
    
    # Blueprintの登録
    register_blueprints(app)
    
    # メインルートの設定
    register_main_route(app)
    
    # データベースの初期化
    init_database(app)

    return app

def init_extensions(app):
    """拡張機能の初期化"""
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    
    login_manager.login_view = 'shared.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

def register_blueprints(app):
    """Blueprintの登録"""
    from shared import shared
    from weight_management import weight
    from reservation_system import reservation
    from admin import admin

    app.register_blueprint(shared, url_prefix='')
    app.register_blueprint(weight, url_prefix='/weight')
    app.register_blueprint(reservation, url_prefix='/reservation')
    app.register_blueprint(admin, url_prefix='/admin')

def register_main_route(app):
    """メインルートの設定"""
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('shared.login'))
        return redirect(url_for('weight.dashboard'))

def init_database(app):
    """データベースの初期化と管理者アカウントの作成"""
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                is_admin=True,
                height=170.0  # デフォルトの身長を設定
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print('管理者アカウントを作成しました')

# アプリケーションのインスタンス作成
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)