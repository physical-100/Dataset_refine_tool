import cv2
import os

# 크롭된 이미지를 저장할 디렉토리 설정
output_dir = "/home/sophie/Desktop/fisheye_crop/images"
label_output_dir = "/home/sophie/Desktop/fisheye_crop/labels"

# 디렉토리가 존재하지 않으면 생성
os.makedirs(output_dir, exist_ok=True)
os.makedirs(label_output_dir, exist_ok=True)

# 작은 크롭을 저장할 별도 디렉토리 설정
small_output_dir = os.path.join(output_dir, "small_crops")
small_label_output_dir = os.path.join(label_output_dir, "small_crops")
os.makedirs(small_output_dir, exist_ok=True)
os.makedirs(small_label_output_dir, exist_ok=True)

# 객체가 없는 이미지를 저장할 별도 디렉토리 설정
no_objects_output_dir = os.path.join(output_dir, "no_objects")
no_objects_label_output_dir = os.path.join(label_output_dir, "no_objects")
os.makedirs(no_objects_output_dir, exist_ok=True)
os.makedirs(no_objects_label_output_dir, exist_ok=True)

# 객체가 없는 이미지 경로를 기록할 텍스트 파일 설정
no_objects_txt_path = os.path.join(output_dir, "no_objects.txt")
no_objects_label_txt_path = os.path.join(label_output_dir, "no_objects.txt")

# 최소 크롭 크기 설정 (참고용, 필요 시 조정 가능)
MIN_CROP_SIZE = 640

# 이미지 소실 비율 임계값 (60% 이상 소실 시 라벨 제거)
THRESHOLD_LOSS_RATIO = 0.6

def crop_image_and_save_label(image_path, label_path, output_dir, label_output_dir, small_output_dir, small_label_output_dir, no_objects_output_dir, no_objects_label_output_dir, no_objects_txt_path, no_objects_label_txt_path, stats):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Warning: Failed to read image {image_path}. Skipping...")
        try:
            os.remove(image_path)
            print(f"Deleted corrupted image: {image_path}")
        except Exception as e:
            print(f"Error deleting {image_path}: {e}")
        return

    h, w, _ = img.shape  # 원본 이미지 크기 (동적 계산)

    # 4분할 섹션 정의 (가로와 세로를 반으로 나눔)
    section_width = w // 2
    section_height = h // 2
    sections = [
        (0, 0, section_width, section_height),      # 상단 왼쪽
        (section_width, 0, w, section_height),      # 상단 오른쪽
        (0, section_height, section_width, h),      # 하단 왼쪽
        (section_width, section_height, w, h)       # 하단 오른쪽
    ]

    with open(label_path, 'r') as file:
        lines = file.readlines()

    if not lines:
        print(f"No objects found in {label_path}. Skipping...")
        return

    base_name = os.path.splitext(os.path.basename(image_path))[0]

    for idx, (x_min, y_min, x_max, y_max) in enumerate(sections):
        # 분할 이미지 추출
        cropped_img = img[y_min:y_max, x_min:x_max]
        cropped_h, cropped_w, _ = cropped_img.shape

        # 크기 확인: 400x400보다 작으면 small_crops 폴더에 저장
        is_small = cropped_w < 400 or cropped_h < 400
        current_output_dir = small_output_dir if is_small else output_dir
        current_label_output_dir = small_label_output_dir if is_small else label_output_dir

        cropped_img_name = f"{base_name}_crop_{idx}.png"
        cropped_img_path = os.path.join(current_output_dir, cropped_img_name)

        # 분할 이미지에 포함된 바운딩 박스 계산
        new_labels = []
        for line in lines:
            parts = line.strip().split()
            class_id = int(parts[0])
            center_x = float(parts[1]) * w
            center_y = float(parts[2]) * h
            bbox_w = float(parts[3]) * w
            bbox_h = float(parts[4]) * h
            
            obj_x_min = int(center_x - bbox_w / 2)
            obj_x_max = int(center_x + bbox_w / 2)
            obj_y_min = int(center_y - bbox_h / 2)
            obj_y_max = int(center_y + bbox_h / 2)

            # 객체가 분할 영역에 부분적으로 포함되는지 확인
            intersection_x_min = max(obj_x_min, x_min)
            intersection_y_min = max(obj_y_min, y_min)
            intersection_x_max = min(obj_x_max, x_max)
            intersection_y_max = min(obj_y_max, y_max)

            # 교차 영역이 없으면 건너뜀
            if intersection_x_max <= intersection_x_min or intersection_y_max <= intersection_y_min:
                continue

            # 교차 영역 크기 계산
            intersection_w = intersection_x_max - intersection_x_min
            intersection_h = intersection_y_max - intersection_y_min
            intersection_area = intersection_w * intersection_h

            # 전체 객체 영역 계산
            object_area = bbox_w * bbox_h

            # 소실 비율 계산 (1 - 교차 영역 / 전체 객체 영역)
            loss_ratio = 1 - (intersection_area / object_area)

            # 60% 이상 소실된 경우 제외 (라벨에서 제거)
            if loss_ratio < THRESHOLD_LOSS_RATIO:  # 60% 이상 포함된 경우만 유지
                # 크롭된 이미지 내에서 정규화된 좌표 계산
                new_x_min = intersection_x_min - x_min
                new_x_max = intersection_x_max - x_min
                new_y_min = intersection_y_min - y_min
                new_y_max = intersection_y_max - y_min

                new_bbox_w = new_x_max - new_x_min
                new_bbox_h = new_y_max - new_y_min

                new_center_x = (new_x_min + new_bbox_w / 2) / cropped_w
                new_center_y = (new_y_min + new_bbox_h / 2) / cropped_h
                new_width = new_bbox_w / cropped_w
                new_height = new_bbox_h / cropped_h

                new_labels.append(f"{class_id} {new_center_x:.6f} {new_center_y:.6f} {new_width:.6f} {new_height:.6f}\n")
            else:
                print(f"Excluded object (>{THRESHOLD_LOSS_RATIO*100}% lost) in {cropped_img_name}")

        # 분할 이미지 개수 증가
        stats['total_crops'] += 1

        # 객체가 있는 경우: 기존 경로에 저장
        if new_labels:
            cv2.imwrite(cropped_img_path, cropped_img)
            label_filename = f"{base_name}_crop_{idx}.txt"
            label_file_path = os.path.join(current_label_output_dir, label_filename)
            with open(label_file_path, 'w') as label_file:
                label_file.writelines(new_labels)
            #print(f"Saved: {label_file_path} (Labels: {len(new_labels)}) in {current_output_dir}")
        # 객체가 없는 경우: no_objects 폴더에 저장하고 경로 기록
        else:
            no_objects_img_path = os.path.join(no_objects_output_dir, cropped_img_name)
            cv2.imwrite(no_objects_img_path, cropped_img)  # no_objects 폴더에 저장
            print(f"Saved image without labels to no_objects: {no_objects_img_path}")

            # no_objects.txt에 경로 기록
            with open(no_objects_txt_path, 'a') as txt_file:
                txt_file.write(f"{no_objects_img_path}\n")
            with open(no_objects_label_txt_path, 'a') as label_txt_file:
                label_txt_file.write(f"{no_objects_img_path}\n")

            # 객체가 없는 이미지 개수 증가
            stats['no_objects_count'] += 1

# 이미지 & 라벨 디렉토리 설정
image_dir = "/home/sophie/Desktop/Fisheye8K/images"
label_dir = "/home/sophie/Desktop/Fisheye8K/labels"

# 통계 정보를 저장할 딕셔너리
stats = {
    'total_images': 0,
    'total_crops': 0,
    'no_objects_count': 0
}

# 기존 no_objects.txt 파일 초기화 (선택 사항)
if os.path.exists(no_objects_txt_path):
    os.remove(no_objects_txt_path)
if os.path.exists(no_objects_label_txt_path):
    os.remove(no_objects_label_txt_path)

for image_filename in os.listdir(image_dir):
    if image_filename.endswith((".png", ".jpg", ".jpeg")):
        image_path = os.path.join(image_dir, image_filename)
        label_path = os.path.join(label_dir, os.path.splitext(image_filename)[0] + ".txt")
        if os.path.exists(label_path):
            stats['total_images'] += 1  # 전체 이미지 개수 증가
            crop_image_and_save_label(image_path, label_path, output_dir, label_output_dir, small_output_dir, small_label_output_dir, no_objects_output_dir, no_objects_label_output_dir, no_objects_txt_path, no_objects_label_txt_path, stats)
        else:
            print(f"Warning: No label file found for {image_filename}")

# 작업 완료 후 통계 정보 출력
print("\n=== Processing Statistics ===")
print(f"Total images processed: {stats['total_images']}")
print(f"Total crops created: {stats['total_crops']}")
print(f"Images with no objects: {stats['no_objects_count']}")