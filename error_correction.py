import os
import shutil

# 클래스 번호와 단어 매핑
class_mapping = {
    0: "bolt_screw", 1: "nut_washers", 2: "bearing_ball", 3: "wire", 4: "fuel_lid", 5: "tire_parts",
    6: "paper_parts", 7: "plastic_parts", 8: "driver", 9: "wrench", 10: "plier_scissors", 11: "hammer",
    12: "drill", 13: "spoon_fork", 14: "paper_cup", 15: "pet_bottle", 16: "can", 17: "pen",
    18: "box", 19: "luggage_tag", 20: "clothes", 21: "concrete_stone", 22: "profile", 23: "plastic_bag",
    24: "leaf", 25: "branch"
}

# 데이터셋 경로
base_path = "./test"  # 본인의 경로로 수정
txt_path = os.path.join(base_path, "labels")
input_file = "mismatched_files.txt"  # 이미 저장된 txt 파일
source_path = "./fod원본/test/labels"  # 원본 데이터 경로

# Case별 파일 리스트 추출
case1_files = []
case2_files = []
case3_files = []

current_case = None
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip()
        if "=== Case 1" in line:
            current_case = "case1"
        elif "=== Case 2" in line:
            current_case = "case2"
        elif "=== Case 3" in line:
            current_case = "case3"
        elif "총" in line or not line:  # 총 개수 라인이나 빈 라인은 건너뜀
            current_case = None
        elif current_case == "case1":
            case1_files.append(line)
        elif current_case == "case2":
            case2_files.append(line)
        elif current_case == "case3":
            case3_files.append(line)

# # Case 1 수정: 모든 클래스 번호를 0번 객체의 클래스 번호로 변경
# def update_case1(file_name, txt_path):
#     txt_full_path = os.path.join(txt_path, file_name + ".txt")
    
#     # .txt 파일 읽기
#     try:
#         with open(txt_full_path, 'r') as f:
#             lines = f.readlines()
#             bbox_data = [list(map(float, line.split())) for line in lines if line.strip()]
#     except FileNotFoundError:
#         print(f"Error: {txt_full_path} 파일이 존재하지 않습니다.")
#         return
    
#     if len(bbox_data) < 2:
#         print(f"Skipping {file_name}: 바운딩 박스가 2개 미만입니다.")
#         return
    
#     # 0번 객체의 클래스 번호 가져오기
#     reference_class = int(bbox_data[0][0])
    
#     # 모든 바운딩 박스의 클래스 번호를 0번 객체와 일치시키기
#     updated_bbox_data = []
#     for bbox in bbox_data:
#         bbox[0] = reference_class
#         updated_bbox_data.append(bbox)
    
#     # 수정된 데이터 저장
#     with open(txt_full_path, 'w') as f:
#         for bbox in updated_bbox_data:
#             f.write(" ".join(map(str, bbox)) + "\n")
#     print(f"Updated {file_name}: All classes set to {reference_class}")

# # Case 2 수정: 파일 이름에 맞는 클래스 번호로 변경
# def update_case2(file_name, txt_path):
#     txt_full_path = os.path.join(txt_path, file_name + ".txt")
    
#     # 파일 이름에서 매핑된 단어 찾기
#     expected_class = None
#     for class_id, word in class_mapping.items():
#         if word in file_name.lower():
#             expected_class = class_id
#             break
    
#     if expected_class is None:
#         print(f"Skipping {file_name}: No class word found in filename")
#         return
    
#     # .txt 파일 읽기
#     try:
#         with open(txt_full_path, 'r') as f:
#             lines = f.readlines()
#             bbox_data = [list(map(float, line.split())) for line in lines if line.strip()]
#     except FileNotFoundError:
#         print(f"Error: {txt_full_path} 파일이 존재하지 않습니다.")
#         return
    
#     if len(bbox_data) != 1:
#         print(f"Skipping {file_name}: 바운딩 박스가 1개가 아닙니다.")
#         return
    
#     # 클래스 번호 수정
#     bbox_data[0][0] = expected_class
    
#     # 수정된 데이터 저장
#     with open(txt_full_path, 'w') as f:
#         for bbox in bbox_data:
#             f.write(" ".join(map(str, bbox)) + "\n")
#     print(f"Updated {file_name}: Class set to {expected_class}")

# Case 3 수정: 원본 경로에서 값을 복사해 덮어쓰기
def update_case3(file_name, txt_path, source_path):
    txt_full_path = os.path.join(txt_path, file_name + ".txt")  # 대상 파일
    source_full_path = os.path.join(source_path, file_name + ".txt")  # 원본 파일
    
    # 원본 파일이 존재하는지 확인
    if not os.path.exists(source_full_path):
        print(f"Error: {source_full_path} 파일이 존재하지 않습니다.")
        return
    
    # 원본 파일 내용을 읽고 대상 파일에 덮어쓰기
    try:
        with open(source_full_path, 'r') as src:
            source_content = src.read()
        
        with open(txt_full_path, 'w') as dst:
            dst.write(source_content)
        print(f"Updated {file_name}: Copied content from {source_full_path}")
    except Exception as e:
        print(f"Error: {file_name} 처리 중 문제 발생 - {str(e)}")

# # Case 1 파일 수정
# print("=== Case 1 수정 시작 ===")
# for file_name in case1_files:
#     update_case1(file_name, txt_path)

# # Case 2 파일 수정
# print("\n=== Case 2 수정 시작 ===")
# for file_name in case2_files:
#     update_case2(file_name, txt_path)

# Case 3 파일 수정
print("\n=== Case 3 수정 시작 ===")
for file_name in case3_files:
    update_case3(file_name, txt_path, source_path)
print(f"총 {len(case3_files)}개 파일 처리 완료")