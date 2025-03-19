import os

def rename_label_files(directory):
    """
    Rename all files in the given directory by replacing 'section' with 'crop' in their filenames.
    """
    for filename in os.listdir(directory):
        if 'section' in filename:
            new_filename = filename.replace('section', 'crop')
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_filename}")

if __name__ == "__main__":
    # Replace 'your_directory_path' with the path to your label files
    directory_path = "/home/sophie/Desktop/fisheye_crop/labels"
    rename_label_files(directory_path)