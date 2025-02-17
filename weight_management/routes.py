# weight_management/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, FloatField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional
from datetime import datetime, timedelta
import re

from . import weight
from .models import WeightRecord
from shared.extensions import db, get_viewing_user_id
from shared.models.user import User
from shared.utils import admin_required

csrf = CSRFProtect()

class ImportDataForm(FlaskForm):
    """データインポートフォーム"""
    username = StringField('ユーザー名', validators=[Optional()])
    height = FloatField('身長', validators=[Optional()])
    gender = SelectField('性別', choices=[('male', '男性'), ('female', '女性')], validators=[Optional()])
    password = PasswordField('パスワード', validators=[Optional()])
    weight_records = TextAreaField('体重記録', validators=[DataRequired()])

# 一般ユーザー向けルート
@weight.route('/')
@login_required
def dashboard():
    """ダッシュボードの表示"""
    user = User.query.get(get_viewing_user_id() or current_user.id)
    today = datetime.now()
    
    return render_template('dashboard.html', 
                         user=user,
                         today=today,
                         current_year=today.year,
                         users=User.query.all() if current_user.is_admin else None)

@weight.route('/data')
@login_required
def get_data():
    """グラフ表示用のデータを取得"""
    user = User.query.get(get_viewing_user_id() or current_user.id)
    period = request.args.get('period', 'total')
    query = WeightRecord.query.filter_by(user_id=user.id)
    
    if period != 'total':
        days = {'1month': 30, '3months': 90, '6months': 180}
        if period in days:
            start_date = datetime.now() - timedelta(days=days[period])
            query = query.filter(WeightRecord.created_at >= start_date)

    records = query.order_by(WeightRecord.created_at).all()
    
    return jsonify({
        'labels': [r.created_at.strftime('%Y-%m-%d') for r in records],
        'weights': [r.weight for r in records],
        'bodyFat': [r.body_fat for r in records],
        'fatMass': [r.calculate_fat_mass() for r in records],
        'leanMass': [r.calculate_lean_mass() for r in records],
        'bmi': [r.calculate_bmi() for r in records]
    })

# 管理者向けルート
@weight.route('/admin/records')
@login_required
@admin_required
def admin_records():
    """体重記録の管理画面"""
    today = datetime.now()
    return render_template('admin/user_list.html',
                         users=User.query.all(),
                         user=current_user,
                         today=today,
                         current_year=today.year)

@weight.route('/admin/users/<int:user_id>/records/data')
@login_required
@admin_required
def get_user_records(user_id):
    """ユーザーの記録データをJSON形式で返す"""
    records = WeightRecord.query.filter_by(user_id=user_id).order_by(WeightRecord.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'records': [{
            'id': r.id,
            'date': r.created_at.strftime('%Y年%m月%d日'),
            'weight': f"{r.weight:.1f}",
            'body_fat': f"{r.body_fat:.1f}" if r.body_fat else None,
            'fat_mass': f"{r.calculate_fat_mass():.1f}" if r.calculate_fat_mass() else None,
            'lean_mass': f"{r.calculate_lean_mass():.1f}" if r.calculate_lean_mass() else None,
            'bmi': f"{r.calculate_bmi():.1f}"
        } for r in records]
    })

@weight.route('/admin/users/<int:user_id>/records/add', methods=['POST'])
@login_required
@admin_required
def add_record(user_id):
    """管理者による記録追加"""
    try:
        record = WeightRecord(
            user_id=user_id,
            weight=float(request.form['weight']),
            body_fat=float(request.form['body_fat']) if request.form['body_fat'] else None,
            created_at=datetime(
                int(request.form['year']),
                int(request.form['month']),
                int(request.form['day'])
            )
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '記録を追加しました'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@weight.route('/admin/records/<int:record_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_record(record_id):
    """記録の削除"""
    record = WeightRecord.query.get_or_404(record_id)
    try:
        db.session.delete(record)
        db.session.commit()
        flash('記録を削除しました', 'success')
    except Exception as e:
        db.session.rollback()
        flash('削除に失敗しました', 'danger')
    return redirect(url_for('weight.admin_records'))

@weight.route('/admin/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_data():
    """データインポート"""
    form = ImportDataForm()
    users = User.query.order_by(User.username).all()
    today = datetime.now()
    
    if form.validate_on_submit():
        try:
            existing_user_id = request.form.get('existing_user_id')
            if existing_user_id:
                user = User.query.get_or_404(existing_user_id)
                if request.form.get('height'): user.height = float(request.form.get('height'))
                if request.form.get('gender'): user.gender = request.form.get('gender')
                if request.form.get('birth_date'): 
                    user.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date()
                if form.password.data: user.set_password(form.password.data)
            else:
                if User.query.filter_by(username=form.username.data).first():
                    flash('このユーザー名は既に使用されています', 'danger')
                    return render_template('admin/import_data.html', 
                                        form=form, users=users, user=current_user,
                                        today=today, current_year=today.year)

                user = User(
                    username=form.username.data,
                    height=float(request.form.get('height')),
                    gender=request.form.get('gender'),
                    birth_date=datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date()
                )
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.flush()

            success_count = 0
            error_lines = []
            for line in form.weight_records.data.strip().split('\n'):
                try:
                    match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d+\.?\d*)\s+(\d+\.?\d*)', line.strip())
                    if match:
                        year, month, day, weight, body_fat = match.groups()
                        db.session.add(WeightRecord(
                            user_id=user.id,
                            weight=float(weight),
                            body_fat=float(body_fat),
                            created_at=datetime(int(year), int(month), int(day))
                        ))
                        success_count += 1
                    else:
                        error_lines.append(line)
                except Exception as e:
                    error_lines.append(line)

            if error_lines:
                flash('以下の行でエラーが発生しました：\n' + '\n'.join(error_lines), 'warning')
            
            if success_count > 0:
                db.session.commit()
                flash(f'{success_count}件のデータを登録しました', 'success')
                return redirect(url_for('weight.admin_records'))
            else:
                db.session.rollback()
                flash('データの登録に失敗しました', 'danger')

        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}', 'danger')
    
    return render_template('admin/import_data.html', 
                         form=form, users=users, user=current_user,
                         today=today, current_year=today.year)

@weight.route('/record', methods=['POST'])
@login_required
def record():
    """一般ユーザーによる記録追加"""
    try:
        record = WeightRecord(
            user_id=current_user.id,
            weight=float(request.form['weight']),
            body_fat=float(request.form['body_fat']) if request.form['body_fat'] else None,
            created_at=datetime(
                int(request.form['year']),
                int(request.form['month']),
                int(request.form['day'])
            )
        )
        db.session.add(record)
        db.session.commit()
        flash('記録を追加しました', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'記録の追加に失敗しました: {str(e)}', 'danger')
    
    return redirect(url_for('weight.dashboard'))