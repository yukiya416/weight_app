import pandas as pd
from datetime import datetime
from app import create_app, db
from shared.models.user import User
from weight_management.models import WeightRecord

def import_user_data(excel_file, sheet_name=None):
    """ユーザーデータをインポート"""
    # Excelファイルを読み込み
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # 最初の行からユーザー情報を取得
    user_data = {
        'username': df.iloc[0]['名前'],  # '名前'列から取得
        'height': float(df.iloc[0]['身長']),  # '身長'列から取得
        'age': int(df.iloc[0]['年齢'])  # '年齢'列から取得
    }
    
    return user_data

def import_weight_records(excel_file, user_id, sheet_name=None):
    """体重記録をインポート"""
    # Excelファイルを読み込み
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # 必要なカラムだけを取得してデータを整形
    records_data = []
    for _, row in df.iterrows():
        # 日付が正しい形式であることを確認
        try:
            date = pd.to_datetime(row['日付'])
            weight = float(row['体重(kg)'])
            body_fat = float(row['体脂肪率(%)'])
            
            record = {
                'user_id': user_id,
                'weight': weight,
                'body_fat': body_fat,
                'created_at': date
            }
            records_data.append(record)
        except (ValueError, KeyError) as e:
            print(f"行の処理中にエラーが発生しました: {e}")
            continue
    
    return records_data

def main(excel_file):
    """メインの実行関数"""
    app = create_app()
    
    with app.app_context():
        try:
            # ユーザーデータのインポート
            user_data = import_user_data(excel_file)
            
            # ユーザーが既に存在するか確認
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"ユーザー {user_data['username']} は既に存在します")
                user = existing_user
            else:
                # 新しいユーザーを作成
                user = User(**user_data)
                db.session.add(user)
                db.session.commit()
                print(f"ユーザー {user_data['username']} を作成しました")
            
            # 体重記録のインポート
            records_data = import_weight_records(excel_file, user.id)
            
            # 記録をバッチで追加
            for record_data in records_data:
                record = WeightRecord(**record_data)
                db.session.add(record)
            
            db.session.commit()
            print(f"{len(records_data)}件の記録をインポートしました")
            
        except Exception as e:
            db.session.rollback()
            print(f"エラーが発生しました: {e}")
            raise

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("使用方法: python import_data.py <excel_file>")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    main(excel_file)