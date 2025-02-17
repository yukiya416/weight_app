from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from . import shared
from shared.extensions import db, set_viewing_user_id, clear_viewing_user
from shared.utils import admin_required
from shared.models.user import User

@shared.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('weight.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('ログインしました', 'success')
            return redirect(url_for('weight.dashboard'))
        
        flash('ユーザー名またはパスワードが間違っています', 'danger')
    
    return render_template('auth/login.html')

@shared.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('weight.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        if password != password_confirm:
            flash('パスワードが一致しません', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('このユーザー名は既に使用されています', 'danger')
            return render_template('auth/register.html')
        
        try:
            user = User(
                username=username,
                height=float(request.form['height']),
                age=int(request.form['age']),
                gender=request.form['gender']
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            flash('アカウントが作成されました。ログインしてください。', 'success')
            return redirect(url_for('shared.login'))
        except Exception as e:
            db.session.rollback()
            flash('アカウントの作成に失敗しました。', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@shared.route('/admin_switch', methods=['POST'])
@login_required
@admin_required
def admin_switch():
    user_id = request.form.get('user_id')
    if not user_id:
        flash('ユーザーIDが指定されていません', 'danger')
        return redirect(url_for('weight.dashboard'))

    target_user = User.query.get_or_404(user_id)
    set_viewing_user_id(target_user.id)
    flash(f'{target_user.username} の情報を表示します', 'success')
    return redirect(url_for('weight.dashboard'))

@shared.route('/logout')
@login_required
def logout():
    clear_viewing_user()
    logout_user()
    flash('ログアウトしました', 'success')
    return redirect(url_for('shared.login'))