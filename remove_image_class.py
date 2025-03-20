import os
from collections import defaultdict
from tqdm import tqdm

# 입력 디렉토리 설정
input_label_dir = '/home/sophie/Desktop/roboflow2/labels/'
input_image_dir = '/home/sophie/Desktop/roboflow2/images/'  # 이미지 디렉토리 추가

# 클래스별 카운트
class_counts = defaultdict(int)

# 클래스 이름 정의
class_names = {
    0: "pedestrian",
    1: "bicycle",
    2: "motorcycle",
    3: "vehicle",
    4: "bus",
    5: "truck"
}

# 삭제된 파일 수 카운트
deleted_files = 0

# 라벨 파일 처리
for label_file in tqdm(os.listdir(input_label_dir), desc="Processing label files"):
    label_path = os.path.join(input_label_dir, label_file)

    # 라벨 파일 읽기
    with open(label_path, 'r') as f:
        labels = f.readlines()

    # 클래스 ID 수집
    class_ids = set()
    for line in labels:
        parts = line.strip().split()
        if len(parts) > 0:
            class_id = int(int(float(parts[0])))
            if 0 <= class_id <= 5:
                class_ids.add(class_id)
                class_counts[class_id] += 1

    # vehicle(3)만 존재하는지 확인
    # if class_ids == {3}:  # vehicle만 포함된 경우
    if not class_ids: 
        # 이미지 파일 경로 생성
        base_name = os.path.splitext(label_file)[0]
        possible_extensions = ['.png', '.jpg', '.jpeg']  # 가능한 이미지 확장자
        image_path = None
        for ext in possible_extensions:
            temp_path = os.path.join(input_image_dir, base_name + ext)
            if os.path.exists(temp_path):
                image_path = temp_path
                break

        # 이미지와 라벨 파일 삭제
        try:
            if image_path:
                os.remove(image_path)
                print(f"Deleted image: {image_path}")
            os.remove(label_path)
            print(f"Deleted label: {label_path}")
            deleted_files += 1
        except Exception as e:
            print(f"Error deleting {label_path} or {image_path}: {e}")

# 클래스별 통계 출력
for cls in range(6):
    print(f"{class_names[cls]} : {class_counts[cls]}")

# 삭제된 파일 수 출력
print(f"\nTotal files deleted (vehicle-only images): {deleted_files}")