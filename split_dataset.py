import os
import random
import shutil

dataset_path = '/home/skyautonet/syan/datasets/archive/exp49_dataset/'
images_path = os.path.join(dataset_path, 'images')
labels_path = os.path.join(dataset_path, 'labels')


train_images_path = os.path.join(images_path, 'train') 
val_images_path = os.path.join(images_path, 'val')      
train_labels_path = os.path.join(labels_path, 'train') 
val_labels_path = os.path.join(labels_path, 'val')      

split_ratio = 0.8

for path in [train_images_path, val_images_path, train_labels_path, val_labels_path]:
    os.makedirs(path, exist_ok=True)


image_files = [f for f in os.listdir(images_path) if f.endswith(('.jpg', '.png', '.jpeg'))]

random.shuffle(image_files)

split_index = int(len(image_files) * split_ratio)

train_files = image_files[:split_index]
val_files = image_files[split_index:]


for file_name in train_files:
    
    shutil.move(os.path.join(images_path, file_name), os.path.join(train_images_path, file_name))
    
    
    label_name = os.path.splitext(file_name)[0] + '.txt'  
    label_path = os.path.join(labels_path, label_name)
    if os.path.exists(label_path):
        shutil.move(label_path, os.path.join(train_labels_path, label_name))
    else:
        print(f"Label file not found for {file_name}: {label_name}")


for file_name in val_files:
   
    shutil.move(os.path.join(images_path, file_name), os.path.join(val_images_path, file_name))
    
    
    label_name = os.path.splitext(file_name)[0] + '.txt' 
    label_path = os.path.join(labels_path, label_name)
    if os.path.exists(label_path):
        shutil.move(label_path, os.path.join(val_labels_path, label_name))
    else:
        print(f"Label file not found for {file_name}: {label_name}")

# Print result
print(f"Dataset Split Completed. Train: {len(train_files)}, Validation: {len(val_files)}")

