import os
from datetime import datetime

def generate_structure(startpath, output_file):
    with open(output_file, 'w') as f:
        f.write(f'# Project Structure - Updated: {datetime.now()}\n\n')
        for root, dirs, files in os.walk(startpath):
            # venv と __pycache__ ディレクトリを除外
            dirs[:] = [d for d in dirs if d not in ['venv', 'weight_env', '__pycache__']]
            
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * (level)
            f.write(f'{indent}├── {os.path.basename(root)}/\n')
            subindent = '│   ' * (level + 1)
            for file in files:
                if not file.endswith('.pyc'):  # .pyc ファイルを除外
                    f.write(f'{subindent}├── {file}\n')

if __name__ == '__main__':
    # スクリプトの場所を基準にしてプロジェクトルートを特定
    project_root = os.path.dirname(os.path.abspath(__file__))
    generate_structure(project_root, os.path.join(project_root, 'project_structure.txt'))