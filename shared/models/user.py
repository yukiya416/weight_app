from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from shared.extensions import db
from datetime import date
from sqlalchemy import Date

class User(UserMixin, db.Model):
    # 基本情報
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    # プロフィール情報
    height = db.Column(db.Float, nullable=True)  # 身長 (cm)
    birth_date = db.Column(db.Date, nullable=True)  # 生年月日
    gender = db.Column(db.String(1), nullable=True)  # 'M' for male, 'F' for female
    
    # 目標値
    target_weight = db.Column(db.Float, nullable=True)      # 目標体重 (kg)
    target_bmi = db.Column(db.Float, nullable=True)         # 目標BMI
    target_body_fat = db.Column(db.Float, nullable=True)    # 目標体脂肪率 (%)
    target_lean_mass = db.Column(db.Float, nullable=True)   # 目標除脂肪体重 (kg)
    
    def set_password(self, password):
        """パスワードをハッシュ化して設定"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """パスワードの確認"""
        return check_password_hash(self.password_hash, password)

    @property
    def display_gender(self):
        """性別の表示用文字列を返す"""
        if self.gender == 'M':
            return '男性'
        elif self.gender == 'F':
            return '女性'
        return '未設定'

    @property
    def age(self):
        """生年月日から年齢を計算して返す"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    def get_recommended_targets(self):
        """身長、年齢、性別に基づいた推奨目標値を計算"""
        if not self.height:
            return None

        # 理想体重（BMI 22をベース）
        ideal_weight = 22 * (self.height / 100) ** 2

        # 性別と年齢に基づく推奨体脂肪率
        current_age = self.age
        if self.gender == 'M':
            if current_age and current_age < 40:
                recommended_fat = 15
            else:
                recommended_fat = 17
        elif self.gender == 'F':
            if current_age and current_age < 40:
                recommended_fat = 25
            else:
                recommended_fat = 27
        else:
            recommended_fat = 22

        # 推奨除脂肪体重
        recommended_lean = ideal_weight * (1 - recommended_fat / 100)

        return {
            'weight': round(ideal_weight, 1),
            'bmi': 22.0,
            'body_fat': recommended_fat,
            'lean_mass': round(recommended_lean, 1)
        }

    def __repr__(self):
        """デバッグ用の文字列表現"""
        return f'<User {self.username}>'