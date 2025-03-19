import os
from tqdm import tqdm

# 경로 설정
source_label_dirs = {
    'train': '/home/sophie/Desktop/Cheonan_Test/labels/train',
    'val': '/home/sophie/Desktop/Cheonan_Test/labels/val'
}
target_label_dirs = {
    'train': '/home/sophie/Desktop/exp49_dataset/labels/train',
    'val': '/home/sophie/Desktop/exp49_dataset/labels/val'
}
backup_dir = '/home/sophie/Desktop/exp49_dataset/label_backup'  # 백업 폴더

# 백업 폴더 생성 (없으면)
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# 타겟 폴더 생성 (없으면)
for dir_name, dir_path in target_label_dirs.items():
    if not os.path.exists(dir_path):
        print("해당 폴더가 없습니다.")

# 모든 소스 .txt 파일 경로 수집 (train과 val 통합)
source_files = []
for split in ['train', 'val']:
    source_dir = source_label_dirs[split]
    source_files.extend([os.path.join(source_dir, f) for f in os.listdir(source_dir) if f.endswith('.txt')])
print(f"Found {len(source_files)} source files")
count = 0
for split in ['train', 'val']:
    target_dir = target_label_dirs[split]


    # 타겟 폴더의 파일 이름 세트
    target_files = {os.path.splitext(f)[0] for f in os.listdir(target_dir) if f.endswith('.txt')}

    # 파일 복사 및 덮어쓰기
    for source_path in tqdm(source_files, desc=f"Processing {split}"):
        file_name = os.path.basename(source_path)
        base_name = os.path.splitext(file_name)[0]  # 확장자 제거한 이름

        if base_name in target_files:
            target_path = os.path.join(target_dir, file_name)
            count+=1

            # 백업 생성
            backup_path = os.path.join(backup_dir, f"{split}_{file_name}")  # split 추가로 구분
            if os.path.exists(target_path):
                with open(target_path, 'r') as f:
                    with open(backup_path, 'w') as b:
                        b.write(f.read())  # 기존 파일 백업

            # 소스 파일로 덮어쓰기
            with open(source_path, 'r') as source_f:
                with open(target_path, 'w') as target_f:
                    target_f.write(source_f.read())

            print(f"Updated {target_path} from {source_path}")

print(f"Process completed. Backups are saved in {backup_dir}")
print(f"변경된 라벨 파일 숫자: {count}")