from shared.extensions import db
from datetime import datetime
from shared.models.user import User  # 共通のUserモデルをインポート

class WeightRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    body_fat = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref=db.backref('weight_records', lazy=True))

    # 計算メソッド
    def calculate_fat_mass(self):
        """体脂肪量を計算"""
        if self.weight is None or self.body_fat is None:
            return None
        return round(self.weight * self.body_fat / 100, 1)

    def calculate_lean_mass(self):
        """除脂肪体重を計算"""
        fat_mass = self.calculate_fat_mass()
        if self.weight is None or fat_mass is None:
            return None
        return round(self.weight - fat_mass, 1)

    def calculate_bmi(self):
        """BMIを計算"""
        if self.weight is None or self.user.height is None:
            return None
        return round(self.weight / ((self.user.height / 100) ** 2), 1)