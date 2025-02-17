# user_import.py
from app import create_app
from shared.models.user import User
from shared.extensions import db
from weight_management.models import WeightRecord
from datetime import datetime

def import_user_data(username, height, password, weight_records_data):
    """ユーザーとその測定記録を一括登録"""
    app = create_app()
    
    with app.app_context():
        try:
            # ユーザーの作成
            user = User(username=username, height=height)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            
            print(f"ユーザーを作成しました - ID: {user.id}")
            
            # 測定記録の整形と登録
            records = []
            for line in weight_records_data.strip().split('\n'):
                try:
                    parts = line.split()
                    date_str = parts[0]
                    weight = float(parts[1])
                    body_fat = float(parts[2])
                    
                    # 日付の形式を統一
                    if '/' in date_str:
                        date = datetime.strptime(date_str, '%Y/%m/%d')
                    else:
                        month, day = map(int, date_str.replace('月', '/').replace('日', '').split('/'))
                        year = 2022 if month >= 8 else 2023  # 年を推測
                        date = datetime(year, month, day)
                    
                    records.append({
                        'user_id': user.id,
                        'weight': weight,
                        'body_fat': body_fat,
                        'created_at': date
                    })
                except Exception as e:
                    print(f"行の処理中にエラー: {line}")
                    print(f"エラー内容: {e}")
                    continue
            
            # レコードの一括登録
            for record in records:
                db.session.add(WeightRecord(**record))
            
            db.session.commit()
            print(f"全ての測定記録（{len(records)}件）を登録しました")
            print(f"\nログイン情報:")
            print(f"ユーザー名: {username}")
            print(f"パスワード: {password}")
            print(f"ユーザーID: {user.id}")
            
        except Exception as e:
            db.session.rollback()
            print(f"エラーが発生しました: {e}")
            raise

if __name__ == '__main__':
    # ユーザー情報
    USERNAME = "アリヤス アイリ"
    HEIGHT = 165.0
    PASSWORD = "password123"
    
    # 測定記録データ
    WEIGHT_RECORDS = """
2022/08/09 84.8 43.3
2022/08/17 83.4 42.9
2022/08/23 82.8 42.7
2022/08/28 82.5 42.7
2022/09/09 81.9 42.2
2022/09/17 80.7 42.1
2022/10/01 80.6 42.4
2022/10/08 80.2 41.7
2022/10/22 79.9 41.8
2022/10/28 79.4 42.1
2022/11/12 78.5 41.7
2022/12/10 77.4 41.4
2023/01/14 78.3 41.2
2023/02/25 77.8 41.1
2023/03/11 77.8 41.0
2023/03/31 78.2 41.2
2023/04/29 77.4 40.3
2023/05/27 77.5 40.2
2023/06/03 75.8 38.7
2023/06/16 75.9 39.1
2023/07/08 75.2 38.9
2023/07/29 74.9 38.7
2023/08/12 74.5 37.9
2023/08/29 74.2 38.1
2023/09/08 74.2 38.5
2023/09/23 73.9 38.5
2023/10/10 73.3 38.1
2023/10/21 72.9 38.5
2023/11/11 72.7 38.0
2023/11/25 72.6 37.5
2023/12/15 72.5 37.6
2023/12/30 73.1 38.0
2024/01/13 72.8 37.7
2024/02/10 73.6 38.2
2024/03/01 72.2 37.8
2024/03/27 73.7 38.4
2024/04/16 73.4 38.1
2024/04/25 73.1 37.7
2024/05/30 73.3 37.5
2024/06/14 73.3 36.2
2024/06/27 73.7 36.8
2024/07/11 72.9 36.8
2024/07/24 73.1 37.0
2024/08/28 73.9 37.0
2024/09/14 74.5 37.8
2024/12/14 76.9 39.5
2024/12/31 77.1 39.9
2025/01/09 76.2 39.5
2025/02/08 76.4 40.0
    """
    
    import_user_data(USERNAME, HEIGHT, PASSWORD, WEIGHT_RECORDS)
