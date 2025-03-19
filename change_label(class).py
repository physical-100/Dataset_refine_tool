import os
from tqdm import tqdm

# 경로 설정
input_label_dir = '/home/sophie/Desktop/Cheonan_Test/labels/val'
backup_dir = '/home/sophie/Desktop/Cheonan_Test/labels/backup'  # 백업 폴더
output_label_dir = '/home/sophie/Desktop/Cheonan_Test/labels/val'  # 수정된 파일 저장 경로 (기존 폴더에 덮어씌움)

# 백업 폴더 생성 (없으면)
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# 클래스 매핑 (기존 ID: 새 ID)
class_mapping = {
    1: 3,  # vehicle → motorcycle
    2: 1,  # bicycle → bicycle
    3: 2   # motorcycle → bicycle
}

# 라벨 파일 순회
for label_file in tqdm(os.listdir(input_label_dir)):
    if label_file.endswith('.txt'):
        label_path = os.path.join(input_label_dir, label_file)

        # 백업 파일 생성
        backup_path = os.path.join(backup_dir, label_file)
        with open(label_path, 'r') as f:
            with open(backup_path, 'w') as b:
                b.write(f.read())  # 기존 파일을 백업

        # 라벨 수정
        with open(label_path, 'r') as f:
            lines = f.readlines()

        modified_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) > 0:
                try:
                    class_id = int(float(parts[0]))  # 실수 → 정수 변환
                    # 클래스 매핑 적용 (0, 4, 5는 변경 없음)
                    new_class_id = class_mapping.get(class_id, class_id)  # 매핑 없으면 원래 값 유지
                    parts[0] = str(float(new_class_id))  # 실수 형태로 유지 (YOLO 형식)
                    modified_lines.append(' '.join(parts))
                except ValueError as e:
                    print(f"Error converting class ID in {label_file}: {e}")
                    modified_lines.append(line.strip())
            else:
                modified_lines.append(line.strip())

        # 수정된 라벨 파일 저장
        with open(label_path, 'w') as f:
            for modified_line in modified_lines:
                f.write(f"{modified_line}\n")

print(f"Label files updated and backed up to {backup_dir}")