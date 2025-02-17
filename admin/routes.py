# admin/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

from shared.models.user import User
from shared.extensions import db
from shared.utils import admin_required
from . import admin

class UserForm(FlaskForm):
    """ユーザー作成・編集フォーム"""
    username = StringField('ユーザー名', validators=[DataRequired()])
    height = FloatField('身長', validators=[Optional()])
    age = IntegerField('年齢', validators=[Optional()])
    gender = SelectField('性別', choices=[('', '未選択'), ('male', '男性'), ('female', '女性')], validators=[Optional()])
    password = PasswordField('パスワード')
    is_admin = BooleanField('管理者権限')

@admin.route('/users')
@login_required
@admin_required
def users():
    """ユーザー一覧表示"""
    users = User.query.order_by(User.username).all()
    return render_template('admin/user_list.html', users=users, user=current_user)

@admin.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """新規ユーザー作成"""
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('このユーザー名は既に使用されています', 'danger')
            return render_template('admin/user_form.html', form=form, user=current_user)

        user = User(
            username=form.username.data,
            height=form.height.data,
            age=form.age.data,
            gender=form.gender.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('ユーザーを作成しました', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash('エラーが発生しました', 'danger')
            
    return render_template('admin/user_form.html', form=form, user=current_user)

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """ユーザー情報編集"""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user_id:
            flash('このユーザー名は既に使用されています', 'danger')
            return render_template('admin/user_form.html', form=form, user=user, edit_mode=True)

        form.populate_obj(user)
        if form.password.data:
            user.set_password(form.password.data)
        
        try:
            db.session.commit()
            flash('ユーザー情報を更新しました', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash('エラーが発生しました', 'danger')
    
    return render_template('admin/user_form.html', form=form, user=user, edit_mode=True)

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """ユーザーの削除"""
    if current_user.id == user_id:
        flash('自分自身は削除できません', 'danger')
        return redirect(url_for('admin.users'))
        
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('管理者ユーザーは削除できません', 'danger')
        return redirect(url_for('admin.users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('ユーザーを削除しました', 'success')
    except Exception as e:
        db.session.rollback()
        flash('エラーが発生しました', 'danger')
    
    return redirect(url_for('admin.users'))