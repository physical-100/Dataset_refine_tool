import os
import shutil

# 이미지와 라벨 폴더 경로
img_dir = "/home/sophie/Desktop/Fisheye8K/images"
label_dir = "/home/sophie/Desktop/Fisheye8K/labels"
mismatch_dir = "/home/sophie/Desktop/Fisheye8K/labels/mismatch"  # 이름이 일치하지 않는 라벨을 저장할 폴더 경로

# mismatch 폴더가 없으면 생성
os.makedirs(mismatch_dir, exist_ok=True)

# 이미지와 라벨 파일 이름 가져오기
img_files = {os.path.splitext(f)[0] for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))}
label_files = {os.path.splitext(f)[0] for f in os.listdir(label_dir) if os.path.isfile(os.path.join(label_dir, f))}
print(f"이미지 파일: {len(img_files)}개, 라벨 파일: {len(label_files)}개")

# 라벨 중 이미지와 이름이 일치하지 않는 파일 찾기
mismatched_labels = label_files - img_files

# 이름이 일치하지 않는 라벨 파일을 mismatch 폴더로 이동
for label in mismatched_labels:
    label_path = os.path.join(label_dir, label + ".txt")  # 라벨 파일 확장자가 .txt라고 가정
    if os.path.exists(label_path):
        shutil.move(label_path, os.path.join(mismatch_dir, os.path.basename(label_path)))

print(f"총 {len(mismatched_labels)}개의 라벨 파일이 이동되었습니다.")

