import os

label_dir = '/home/sophie/Desktop/roboflow2/labels/'

for filename in os.listdir(label_dir):
    if filename.endswith('.txt'):
        label_path = os.path.join(label_dir, filename)
        
        with open(label_path, 'r') as file:
            lines = file.readlines()
        
        new_lines = [line for line in lines if line.strip().split()[0] != '3.0']
        
        with open(label_path, 'w') as file:
            file.writelines(new_lines)

print(label_dir,"3: Vehicle Class is Removed.")
