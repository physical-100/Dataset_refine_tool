import os
from collections import defaultdict
from tqdm import tqdm

input_label_dir = '/home/sophie/Desktop/Cheonan_Test/labels/val' 

class_counts = defaultdict(int)

class_names = {
    0: "pedestrian",
    1: "bicycle",
    2: "motorcycle",
    3: "vehicle",
    4: "bus",
    5: "truck"
}

for label_file in tqdm(os.listdir(input_label_dir)):
    label_path = os.path.join(input_label_dir, label_file)

    with open(label_path, 'r') as f:
        labels = f.readlines()

        for line in labels:
        
            parts = line.strip().split()
            if len(parts) > 0:
                class_id = int(int(float(parts[0])))
                if 0 <= class_id <= 5: 
                    class_counts[class_id] += 1  

for cls in range(6):
    print(f"{class_names[cls]} : {class_counts[cls]}")