###사용법###
# python refine_tool.py <dataset_base_path>
# 예: python refine_tool.py ./refined/train
# 좌클릭: 바운딩 박스 클릭 시 수정/삭제 팝업 표시
# 우클릭: add ambiguity /add box 팝업 표시
#      A: 새로운 바운딩 박스 추가 (4가지 점을 클릭해서 추가)
# M: 선택한 바운딩 박스 수정 (4가지 점을 클릭해서 수정)
# R: 선택한 바운딩 박스 삭제
# L: 현재 이미지의 라벨 정보 표시
# S: 현재 이미지의 크기 표시
    # Esc: 팝업 창 닫기 
# 좌우 화살표: 이전/다음 이미지로 이동
# 창 닫을 때 진행률 저장

import cv2, os, logging, json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk

# 로깅 설정
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 클래스 번호와 단어 매핑
class_mapping = {
    0: "pedestrian", 1: "bicycle", 2: "motorcycle", 3: "vehicle", 4: "bus", 5: "truck"
}

class REFINE:
    def __init__(self, imgName, img_dir, label_dir):
        self.imgName = imgName
        self.bbox = []
        self.img = None
        self.img_dir = img_dir  # 인자로 받은 경로
        self.label_dir = label_dir  # 인자로 받은 경로
    
    def readImg(self, extensions=['.png', '.jpeg', '.jpg']):
        try:
            img_full_path = None
            for ext in extensions:
                temp_path = os.path.join(self.img_dir, self.imgName + ext)
                if os.path.exists(temp_path):
                    img_full_path = temp_path
                    break
            
            if img_full_path is None:
                raise FileNotFoundError(f"Image file not found for {self.imgName} with extensions {extensions}")

            self.img = cv2.imread(img_full_path)
            if self.img is None:
                raise ValueError(f"Failed to load image: {img_full_path}")

            txt_full_path = os.path.join(self.label_dir, self.imgName + '.txt')
            if not os.path.exists(txt_full_path):
                raise FileNotFoundError(f"Label file not found at: {txt_full_path}")
            with open(txt_full_path, 'r') as f:
                for line in f:
                    self.bbox += [list(map(float, line.split()))]
            logging.info(f"Successfully loaded image and labels for {self.imgName} from {img_full_path}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            logging.error(f"File not found error: {e}")
        except Exception as e:
            print(f"Unexpected error while reading files: {e}")
            logging.error(f"Unexpected error: {e}")

    def draw(self):
        self.readImg()
        if self.img is None:
            print("Error: Image data is missing.")
            logging.error(f"Image data is missing for {self.imgName}")
            return None
        if not self.bbox:
            print("Warning: No bounding box data found, displaying image only.")
            logging.info(f"No bounding box data for {self.imgName}")
            return self.img, self.bbox, self.img.shape[1], self.img.shape[0]

        height, width, _ = self.img.shape
        img_copy = self.img.copy()

        for i, box in enumerate(self.bbox):
            cls, x, y, w, h = box
            x, y, w, h = x * width, y * height, w * width, h * height
            x1, y1 = int(x - w / 2), int(y - h / 2)
            x2, y2 = int(x + w / 2), int(y + h / 2)

            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img_copy, str(i), (x1, y1 - 5 if y1 - 5 > 10 else y1 + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        logging.info(f"Drew bounding boxes for {self.imgName}")
        return img_copy, self.bbox, width, height

    def convert(self, width, height, coordinates):
        try:
            x1, y1, x2, y2 = coordinates
            if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
                raise ValueError("Coordinates out of image bounds")
            dw, dh = 1./width, 1./height
            x, y = (x1 + x2)/2.0, (y1 + y2)/2.0
            w, h = x2 - x1, y2 - y1
            x, w, y, h = x*dw, w*dw, y*dh, h*dh
            return x, y, w, h
        except ValueError as e:
            print(f"Error in coordinate conversion: {e}")
            logging.error(f"Coordinate conversion error: {e}")
            return None

    def update_labels(self, new_bbox):
        try:
            with open(os.path.join(self.label_dir, self.imgName + '.txt'), 'w') as f:
                for box in new_bbox:
                    f.write(f"{float(box[0])} {' '.join(map(str, box[1:]))}\n")
            print("SAVED!!!")
            logging.info(f"Updated labels for {self.imgName}")
        except Exception as e:
            print(f"Error saving file: {e}")
            logging.error(f"Save error: {e}")

class GUI:
    def __init__(self, root, base_path, img_dir, label_dir):
        self.root = root
        self.root.title("Dataset Refinement Tool")
        self.base_path = base_path
        self.img_dir = img_dir  # 인자로 받은 경로
        self.label_dir = label_dir  # 인자로 받은 경로
        
        # 이미지 목록 가져오기
        self.images = [os.path.splitext(f)[0] for f in os.listdir(self.img_dir) if f.endswith(('.jpeg', '.png', '.jpg'))]
        
        # 프로그레스 로드
        self.progress_file = 'progress.json'
        self.load_progress()

        # ambiguous_images.txt 경로 설정
        self.ambiguous_file = os.path.join(base_path, 'ambiguous_images.txt')

        # 상단 프레임 (파일 이름, 진행률)
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, pady=10)

        # 파일 이름 표시
        self.filename_label = tk.Label(self.top_frame, text="", font=("Arial", 12))
        self.filename_label.pack(side=tk.TOP)

        # 진행률 표시
        self.progress_label = tk.Label(self.top_frame, text=f"{self.current_idx + 1}/{len(self.images)}")
        self.progress_label.pack(side=tk.TOP, pady=5)

        # 이미지 미리보기 캔버스
        self.canvas = tk.Canvas(root, width=600, height=600)
        self.canvas.pack(side=tk.TOP)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # 버튼 프레임 (하단에 고정)
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.BOTTOM, pady=10)
        tk.Button(self.button_frame, text="Label", command=self.check_label).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Size", command=self.check_size).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=5)

        # 단축키 바인딩
        self.root.bind("m", lambda event: self.start_modify(self.last_clicked_idx) if self.last_clicked_idx is not None else None)
        self.root.bind("r", lambda event: self.remove_bbox(self.last_clicked_idx) if self.last_clicked_idx is not None else None)
        self.root.bind("a", lambda event: self.start_add())
        self.root.bind("<Left>", lambda event: self.prev_image())
        self.root.bind("<Right>", lambda event: self.next_image())
        self.root.bind("l", lambda event: self.check_label())
        self.root.bind("s", lambda event: self.check_size())

        self.last_clicked_idx = None
        self.popup = None
        self.modify_mode = False
        self.modify_points = []
        self.temp_lines = []
        self.action = None
        self.width = 0  # 초기 너비
        self.height = 0  # 초기 높이

        # 초기 이미지 로드
        self.load_image()

    def load_progress(self):
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                if 'base_path' in progress:
                    old_progress = {
                        progress['base_path']: {
                            'current_idx': progress['current_idx'],
                            'total_files': progress['total_files']
                        }
                    }
                    progress = old_progress
                    with open(self.progress_file, 'w') as f:
                        json.dump(progress, f)
                    logging.info("Converted old progress format to new dictionary format")
            else:
                progress = {}

            if self.base_path in progress and progress[self.base_path].get('total_files') == len(self.images):
                self.current_idx = progress[self.base_path].get('current_idx', 0)
            else:
                progress[self.base_path] = {
                    'current_idx': 0,
                    'total_files': len(self.images)
                }
                self.current_idx = 0
                with open(self.progress_file, 'w') as f:
                    json.dump(progress, f)
                logging.info(f"Initialized new path {self.base_path} in progress.json")
        except Exception as e:
            print(f"Error loading progress: {e}")
            logging.error(f"Progress load error: {e}")
            self.current_idx = 0

    def save_progress(self):
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                if 'base_path' in progress:
                    old_progress = {
                        progress['base_path']: {
                            'current_idx': progress['current_idx'],
                            'total_files': progress['total_files']
                        }
                    }
                    progress = old_progress
            else:
                progress = {}

            progress[self.base_path] = {
                'current_idx': self.current_idx,
                'total_files': len(self.images)
            }

            with open(self.progress_file, 'w') as f:
                json.dump(progress, f)
            logging.info(f"Saved progress: {self.current_idx}/{len(self.images)} for {self.base_path}")
        except Exception as e:
            print(f"Error saving progress: {e}")
            logging.error(f"Progress save error: {e}")

    def on_closing(self):
        self.save_progress()
        self.root.destroy()

    def load_image(self):
        if not self.images:
            messagebox.showerror("Error", "No images found in dataset folder!")
            return

        self.hide_popup()
        self.modify_mode = False
        self.modify_points = []
        self.clear_temp_lines()
        self.action = None
        self.refine = REFINE(self.images[self.current_idx], self.img_dir, self.label_dir)
        result = self.refine.draw()
        if result is None:
            self.next_image()
            return

        img, self.bbox, self.width, self.height = result
        
        self.canvas.config(width=self.width, height=self.height)
        self.root.geometry(f"{self.width + 400}x{self.height + 200}")
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        self.img_tk = ImageTk.PhotoImage(img_pil)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
        
        self.filename_label.config(text=f"File: {self.images[self.current_idx]}")
        self.progress_label.config(text=f"{self.current_idx + 1}/{len(self.images)}")

    def prev_image(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.load_image()
            self.save_progress()

    def next_image(self):
        if self.current_idx < len(self.images) - 1:
            self.current_idx += 1
            self.load_image()
            self.save_progress()

    def check_size(self):
        """현재 이미지의 크기를 표시"""
        if self.width and self.height:
            messagebox.showinfo("Image Size", f"Width: {self.width}px, Height: {self.height}px")
        else:
            messagebox.showwarning("Image Size", "Image not loaded yet or size unavailable.")

    def check_label(self):
        """현재 이미지의 라벨 값을 커스텀 창에 한 줄에 표시"""
        if not self.images:
            messagebox.showerror("Error", "No images found in dataset folder!")
            return

        # 현재 이미지 이름
        img_name = self.images[self.current_idx]
        label_path = os.path.join(self.label_dir, img_name + '.txt')  # self.label_dir 사용

        try:
            if not os.path.exists(label_path):
                messagebox.showwarning("Label Info", f"Label file not found for {img_name}")
                return

            # 라벨 파일 읽기
            with open(label_path, 'r') as f:
                lines = f.readlines()

            if not lines:
                messagebox.showinfo("Label Info", f"No labels found for {img_name}")
                return

            # 라벨 정보 포맷팅 (한 줄에 표시)
            label_info = [f"Labels for {img_name}: "]
            for idx, line in enumerate(lines):
                parts = list(map(float, line.strip().split()))
                if len(parts) != 5:
                    label_info.append(f"Box {idx}: Invalid format | ")
                    continue
                class_id, x, y, w, h = parts
                class_name = class_mapping.get(int(class_id), f"Unknown Class ({int(class_id)})")
                label_info.append(f"Box {idx}: {class_name} (x={x:.3f}, y={y:.3f}, w={w:.3f}, h={h:.3f}) | ")

            # 커스텀 창 생성
            label_window = tk.Toplevel(self.root)
            label_window.title("Label Info")
            label_window.geometry("800x200")  # 창 크기 수동 설정

            # 스크롤바와 Text 위젯 결합
            text_frame = tk.Frame(label_window)
            text_frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            text_widget = tk.Text(text_frame, wrap=tk.NONE, yscrollcommand=scrollbar.set, height=5)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)

    
            text_widget.insert(tk.END, "\n".join(label_info))
            text_widget.config(state=tk.DISABLED)  # 텍스트 위젯 읽기 전용 설정

            # 창 닫기 버튼
            tk.Button(label_window, text="Close", command=label_window.destroy).pack(pady=5)

            # Esc 키 바인딩
            label_window.bind("<Escape>", lambda event: label_window.destroy())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read label file: {e}")
            logging.error(f"Error reading label file for {img_name}: {e}")

    def on_left_click(self, event):
        if self.modify_mode:
            self.modify_points.append((event.x, event.y))
            self.draw_temp_line(event.x, event.y)
            if len(self.modify_points) == 4:
                if self.action == 'modify':
                    self.finish_modify()
                elif self.action == 'add':
                    self.finish_add()
            return

        self.hide_popup()
        x, y = event.x, event.y
        for i, box in enumerate(self.bbox):
            cls, bx, by, bw, bh = box
            bx, by, bw, bh = bx * self.width, by * self.height, bw * self.width, bh * self.height
            x1, y1 = bx - bw / 2, by - bh / 2
            x2, y2 = bx + bw / 2, by + bh / 2
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.last_clicked_idx = i
                self.show_popup(event.x, event.y)
                break
        else:
            self.last_clicked_idx = None

    def on_right_click(self, event):
        self.hide_popup()
        self.show_right_click_popup(event.x, event.y)

    def show_popup(self, x, y):
        self.popup = tk.Toplevel(self.root)
        self.popup.wm_overrideredirect(True)
        self.popup.geometry(f"+{self.root.winfo_x() + x}+{self.root.winfo_y() + y + 50}")
        tk.Button(self.popup, text="Modify (M)", command=lambda: self.start_modify(self.last_clicked_idx)).pack(fill=tk.X)
        tk.Button(self.popup, text="Remove (R)", command=lambda: self.remove_bbox(self.last_clicked_idx)).pack(fill=tk.X)

    def show_right_click_popup(self, x, y):
        self.popup = tk.Toplevel(self.root)
        self.popup.wm_overrideredirect(True)
        self.popup.geometry(f"+{self.root.winfo_x() + x}+{self.root.winfo_y() + y + 50}")
        tk.Button(self.popup, text="Add Box (A)", command=self.start_add).pack(fill=tk.X)
        tk.Button(self.popup, text="Add to Ambiguous", command=self.add_to_ambiguous).pack(fill=tk.X)

    def hide_popup(self):
        if self.popup:
            self.popup.destroy()
            self.popup = None

    def start_modify(self, idx):
        if idx is None:
            return
        self.hide_popup()
        self.modify_mode = True
        self.modify_idx = idx
        self.modify_points = []
        self.clear_temp_lines()
        self.action = 'modify'
        print("Click 4 points to define the new bounding box (top-left, top-right, bottom-right, bottom-left)")

    def start_add(self):
        self.hide_popup()
        class_options = "\n".join([f"{k}: {v}" for k, v in class_mapping.items()])
        class_input = simpledialog.askstring(
            "Class Input", 
            f"Enter class number for the new bounding box:\n{class_options}", 
            parent=self.root
        )
        if class_input is None or not class_input.isdigit() or int(class_input) not in class_mapping:
            print("Add cancelled: No valid class number provided")
            return
        self.new_class = float(class_input)
        
        self.modify_mode = True
        self.modify_points = []
        self.clear_temp_lines()
        self.action = 'add'
        print("Click 4 points to define the new bounding box for addition")

    def draw_temp_line(self, x, y):
        if len(self.modify_points) > 1:
            prev_x, prev_y = self.modify_points[-2]
            line = self.canvas.create_line(prev_x, prev_y, x, y, fill="red", dash=(4, 2))
            self.temp_lines.append(line)
        if len(self.modify_points) == 4:
            first_x, first_y = self.modify_points[0]
            last_line = self.canvas.create_line(self.modify_points[-1][0], self.modify_points[-1][1], first_x, first_y, fill="red", dash=(4, 2))
            self.temp_lines.append(last_line)

    def clear_temp_lines(self):
        for line in self.temp_lines:
            self.canvas.delete(line)
        self.temp_lines = []

    def finish_modify(self):
        if len(self.modify_points) != 4:
            print("Error: Exactly 4 points are required")
            self.modify_mode = False
            return

        x_coords = [p[0] for p in self.modify_points]
        y_coords = [p[1] for p in self.modify_points]
        x1, x2 = min(x_coords), max(x_coords)
        y1, y2 = min(y_coords), max(y_coords)
        coordinates = (x1, y1, x2, y2)

        new_bbox = self.bbox[:]
        converted = self.refine.convert(self.width, self.height, coordinates)
        if converted:
            new_bbox[self.modify_idx] = [float(self.bbox[self.modify_idx][0]), *converted]
            self.refine.update_labels(new_bbox)
            self.bbox = new_bbox
            self.load_image()
            self.save_progress()
        self.modify_mode = False
        self.modify_points = []
        self.clear_temp_lines()

    def finish_add(self):
        if len(self.modify_points) != 4:
            print("Error: Exactly 4 points are required")
            self.modify_mode = False
            return

        x_coords = [p[0] for p in self.modify_points]
        y_coords = [p[1] for p in self.modify_points]
        x1, x2 = min(x_coords), max(x_coords)
        y1, y2 = min(y_coords), max(y_coords)
        coordinates = (x1, y1, x2, y2)

        converted = self.refine.convert(self.width, self.height, coordinates)
        if converted:
            new_bbox = self.bbox + [[self.new_class, *converted]]
            self.refine.update_labels(new_bbox)
            self.bbox = new_bbox
            self.load_image()
            self.save_progress()
        self.modify_mode = False
        self.modify_points = []
        self.clear_temp_lines()

    def add_to_ambiguous(self):
        try:
            with open(self.ambiguous_file, 'a') as f:
                f.write(f"{self.images[self.current_idx]}\n")
            print(f"Added {self.images[self.current_idx]} to ambiguous list at {self.ambiguous_file}")
            logging.info(f"Added {self.images[self.current_idx]} to {self.ambiguous_file}")
            self.hide_popup()
        except Exception as e:
            print(f"Error saving to ambiguous list: {e}")
            logging.error(f"Error saving to ambiguous list: {e}")

    def remove_bbox(self, idx):
        if idx is None:
            return
        if messagebox.askyesno("Confirm", f"Remove bounding box {idx}?"):
            new_bbox = [box for i, box in enumerate(self.bbox) if i != idx]
            self.refine.update_labels(new_bbox)
            self.bbox = new_bbox
            self.load_image()
            self.save_progress()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <dataset_base_path>")
        sys.exit(1)

    base_path = sys.argv[1]  # 예: './refined/train'
    img_dir = os.path.join(base_path, 'images')
    label_dir = os.path.join(base_path, 'labels')
    # img_dir = os.path.join(base_path, 'images/train')
    # label_dir = os.path.join(base_path, 'labels/train')

    root = tk.Tk()
    app = GUI(root, base_path, img_dir, label_dir)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # 창 닫을 때 진행률 저장
    root.mainloop()