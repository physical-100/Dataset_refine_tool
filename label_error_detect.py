import os

# 클래스 번호와 단어 매핑
class_mapping = {
    0: "bolt_screw", 1: "nut_washers", 2: "bearing_ball", 3: "wire", 4: "fuel_lid", 5: "tire_parts",
    6: "paper_parts", 7: "plastic_parts", 8: "driver", 9: "wrench", 10: "plier_scissors", 11: "hammer",
    12: "drill", 13: "spoon_fork", 14: "paper_cup", 15: "pet_bottle", 16: "can", 17: "pen",
    18: "box", 19: "luggage_tag", 20: "clothes", 21: "concrete_stone", 22: "profile", 23: "plastic_bag",
    24: "leaf", 25: "branch"
}

# 데이터셋 경로 (사용자 지정 필요)
base_path = "./test"  # 예: './refined/train'
img_path = os.path.join(base_path, "images")
txt_path = os.path.join(base_path, "labels")

# 결과 저장용 리스트
case1_files = []  # 바운딩 박스 2개 이상이고 클래스 번호가 서로 다른 경우
case2_files = []  # 바운딩 박스 1개인데 파일 이름과 일치하지 않는 경우
case3_files = []  # 파일 이름에 단어가 포함되지 않는 경우
# case4_files = []  # 클래스가 사라지고 바로 바운딩 박스가 나오는 경우

# .txt 파일 목록 가져오기 (3707개만 처리)
images = [f[:-5] for f in os.listdir(img_path) if f.endswith('.jpeg')]
change_images = images[0:3707]
print(f"마지막 이미지 이름: {change_images[-1]}")

# Step 1: Case 1과 Case 2 처리
for txt_name in change_images:
    txt_full_path = os.path.join(txt_path, txt_name + ".txt")
    
    # .txt 파일 읽기
    try:
        with open(txt_full_path, 'r') as f:
            lines = f.readlines()
            bbox_data = [list(map(float, line.split())) for line in lines if line.strip()]
    except FileNotFoundError:
        print(f"Warning: {txt_full_path} 파일이 존재하지 않습니다.")
        continue
    
    # 빈 파일은 제외
    if not bbox_data:
        continue
    # elif bbox_data[1][0]== ".":
    #         case4_files.append(txt_name)
    #         continue
    # # 클래스 번호 추출
    else:
        class_numbers = [int(bbox[0]) for bbox in bbox_data]
    
        # Case 1: 바운딩 박스 2개 이상이고 클래스 번호가 서로 다른 경우
        if len(bbox_data) >= 2:
            if len(set(class_numbers)) > 1:  # 클래스 번호가 모두 같지 않으면 추가
                case1_files.append(txt_name)
            continue
        
        # Case 2: 바운딩 박스 1개인데 파일 이름과 일치하지 않는 경우
        elif len(bbox_data) == 1:
            # 파일 이름에서 매핑된 단어 찾기
            matched_word = None
            expected_class = None
            for class_id, word in class_mapping.items():
                if word in txt_name.lower():  # 대소문자 무시
                    matched_word = word
                    expected_class = class_id
                    break
            if matched_word and class_numbers[0] != expected_class:
                case2_files.append(txt_name)
            if not matched_word:
                #crop 이름을 가진 이미지중 class가 0이 아닌 것은 원래 라벨링 되어 있던 것
                if class_numbers[0] == 0:
                    case3_files.append(txt_name)

# 결과 출력
print("=== Case 1: 바운딩 박스 2개 이상이고 클래스 번호가 서로 다른 파일 ===")
for fname in case1_files:
    print(fname)
print(f"총 {len(case1_files)}개\n")

print("=== Case 2: 바운딩 박스 1개인데 파일 이름과 일치하지 않는 파일 ===")
for fname in case2_files:
    print(fname)
print(f"총 {len(case2_files)}개\n")

print("=== Case 3: 파일 이름에 단어가 포함되지 않는 파일 (빈 파일 제외) ===")
for fname in case3_files:
    print(fname)
print(f"총 {len(case3_files)}개\n")

# 결과를 파일로 저장
with open("mismatched_files.txt", "w") as f:
    f.write("=== Case 1: 바운딩 박스 2개 이상이고 클래스 번호가 서로 다른 파일 ===\n")
    f.writelines(f"{fname}\n" for fname in case1_files)
    f.write(f"총 {len(case1_files)}개\n\n")
    
    f.write("=== Case 2: 바운딩 박스 1개인데 일치하지 않는 파일 ===\n")
    f.writelines(f"{fname}\n" for fname in case2_files)
    f.write(f"총 {len(case2_files)}개\n\n")
    
    f.write("=== Case 3: 파일 이름에 단어가 포함되지 않는 파일 (빈 파일 제외) ===\n")
    f.writelines(f"{fname}\n" for fname in case3_files)
    f.write(f"총 {len(case3_files)}개\n")

    # f.write("=== Case 4: 클래스가 사라진 파일들 ===\n")
    # f.writelines(f"{fname}\n" for fname in case4_files)
    # f.write(f"총 {len(case4_files)}개\n")