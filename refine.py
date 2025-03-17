# import cv2, sys, os, argparse

# class REFINE:
#     def __init__(self, imgName, idx):
#         self.imgName = imgName
#         self.bbox = []
#         self.img = None
#         self.idx = idx
    
#     def readImg(self):
#         imgPath = './refined/train/images/'
#         txtPath = './refined/train/labels/'
        
#         try:
#             self.img = cv2.imread(imgPath + self.imgName + '.jpeg')

#             with open(txtPath + self.imgName + '.txt', 'r') as f:
#                 for line in f:
#                     self.bbox += [list(map(float, line.split()))]
#         except:
#             print("The image file or txt file does not exsit!!!")

#     def draw(self):
#         self.readImg()

#         if self.img is None or not self.bbox:
#             print("The image file or txt file does not exsit!!!")
#             return

#         height, width, _ = self.img.shape

#         print(width, height)

#         for i, box in enumerate(self.bbox):
#             print(*self.bbox[i])
#             if self.idx and i in self.idx:
#                 cls, x, y, w, h = box
#                 x, y, w, h = x * width, y * height, w * width, h * height

#                 x1, y1 = int(x - w / 2), int(y - h / 2)
#                 x2, y2 = int(x + w / 2), int(y + h / 2)

#                 color = (0, 255, 0)
#                 thickness = 2

#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 font_scale = 0.5
#                 font_thickness = 2

#                 label_size = cv2.getTextSize(str(i), font, font_scale, font_thickness)[0]
#                 label_x = x1
#                 label_y = y1 - 5 if y1 - 5 > 10 else y1 + label_size[1] + 5

#                 cv2.rectangle(self.img, (x1, y1), (x2, y2), color, thickness)
#                 cv2.putText(self.img, str(i), (label_x, label_y), font, font_scale, (0, 0, 255), font_thickness)

#             elif not self.idx:
#                 cls, x, y, w, h = box
                
#                 x, y, w, h = x * width, y * height, w * width, h * height

#                 x1, y1 = int(x - w / 2), int(y - h / 2)
#                 x2, y2 = int(x + w / 2), int(y + h / 2)

#                 color = (0, 255, 0)
#                 thickness = 2
                
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 font_scale = 0.5
#                 font_thickness = 2

#                 label_size = cv2.getTextSize(str(i), font, font_scale, font_thickness)[0]
#                 label_x = x1
#                 label_y = y1 - 5 if y1 - 5 > 10 else y1 + label_size[1] + 5

#                 cv2.rectangle(self.img, (x1, y1), (x2, y2), color, thickness)
#                 cv2.putText(self.img, str(i), (label_x, label_y), font, font_scale, (0, 0, 255), font_thickness)

#         cv2.imshow('imgbbox', self.img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()

#     def convert(self, width, height, coordinate):
#         x1, y1, x2, y2 = coordinate
#         dw, dh = 1./width, 1./height
        
#         x, y = (x1 + x2)/2.0, (y1 + y2)/2.0
#         w, h = x2 - x1, y2 - y1
#         x, w, y, h = x*dw, w*dw, y*dh, h*dh

#         return x, y, w, h

#     def modify(self):
#         self.readImg()
#         newbbox = []

#         if self.img is None or not self.bbox:
#             print("The image file or txt file does not exsit!!!")
#             return

#         if self.idx:
#             for i, box in enumerate(self.bbox):
#                 cls = int(box[0])
#                 if i in self.idx:
#                     newbbox += [[cls, *box[1:]]]
                
#         else:
#             for i, box in enumerate(self.bbox):
#                 cls = int(box[0])
#                 newbbox += [[cls, *box[1:]]]

#         print("bbox\n", *newbbox)
#         with open('./refined/train/labels/' + self.imgName + '.txt', 'w') as f:
#             for box in newbbox:
#                 f.write(" ".join(map(str, box)) + '\n')
#         print("SAVED!!!")

#     def remove(self):
#         imgPath = './refined/train/images/'
#         txtPath = './refined/train/labels/'

#         try:
#             os.remove(imgPath + self.imgName + '.jpeg')
#             print("Remove image file!!!")
#         except:
#             print("The image file does not exist!!!")

#         try:
#             os.remove(txtPath + self.imgName + '.txt')
#             print("Remove txt file!!!")
#         except:
#             print("The txt file does not exist!!!")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-img', '--imgName', type=str, help='image name')
#     parser.add_argument('-o', '--object', type = str, default=None, help='object name')
#     parser.add_argument('-n', '--numbering', nargs="+", type=str, default=[], help='image number')
#     parser.add_argument('-id', '--label_index', nargs="+", type=int, default = [], help='label index ex) 1 2')
#     parser.add_argument('-m', '--mode', type=str, default='check', help='modify label')
#     args = parser.parse_args()

#     # hanla_0604_datasets_train_wrench_339_crop_2 여기까지함

#     imgName = args.imgName + '_' + args.object + '_' + args.numbering[0] + '_crop_' + args.numbering[1]
    
#     refine = REFINE(imgName, args.label_index)
#     if args.mode == 'check':
#         refine.draw() 
#     elif args.mode == 'modify':
#         refine.modify()
#     elif args.mode == 'remove':
#         refine.remove()


import cv2, sys, os, argparse
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class REFINE:
    def __init__(self, imgName, idx):
        self.imgName = imgName
        self.bbox = []
        self.img = None
        self.idx = idx
    
    def readImg(self):
        imgPath = './refined/train/images/'
        txtPath = './refined/train/labels/'
        
        try:
            img_full_path = imgPath + self.imgName + '.jpeg'
            if not os.path.exists(img_full_path):
                raise FileNotFoundError(f"Image file not found at: {img_full_path}")
            self.img = cv2.imread(img_full_path)
            if self.img is None:
                raise ValueError(f"Failed to load image: {img_full_path}")

            txt_full_path = txtPath + self.imgName + '.txt'
            if not os.path.exists(txt_full_path):
                raise FileNotFoundError(f"Label file not found at: {txt_full_path}")
            with open(txt_full_path, 'r') as f:
                for line in f:
                    self.bbox += [list(map(float, line.split()))]
            logging.info(f"Successfully loaded image and labels for {self.imgName}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            logging.error(f"File not found error: {e}")
        except Exception as e:
            print(f"Unexpected error while reading files: {e}")
            logging.error(f"Unexpected error: {e}")

    def draw(self):
        self.readImg()

        if self.img is None or not self.bbox:
            print("Cannot proceed: Image or bounding box data is missing.")
            return

        height, width, _ = self.img.shape
        print(f"Image dimensions: {width}x{height}")

        for i, box in enumerate(self.bbox):
            print(f"Box {i}: {box}")
            if self.idx and i in self.idx or not self.idx:
                cls, x, y, w, h = box
                x, y, w, h = x * width, y * height, w * width, h * height

                x1, y1 = int(x - w / 2), int(y - h / 2)
                x2, y2 = int(x + w / 2), int(y + h / 2)

                color = (0, 255, 0)
                thickness = 2

                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 2

                label_size = cv2.getTextSize(str(i), font, font_scale, font_thickness)[0]
                label_x = x1
                label_y = y1 - 5 if y1 - 5 > 10 else y1 + label_size[1] + 5

                cv2.rectangle(self.img, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(self.img, str(i), (label_x, label_y), font, font_scale, (0, 0, 255), font_thickness)

        cv2.imshow('imgbbox', self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        logging.info(f"Drew bounding boxes for {self.imgName}")

    def convert(self, width, height, coordinate):
        try:
            x1, y1, x2, y2 = map(int, coordinate)
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

    def modify(self):
        self.readImg()
        newbbox = []

        if self.img is None or not self.bbox:
            print("Cannot proceed: Image or bounding box data is missing.")
            return

        height, width, _ = self.img.shape

        if self.idx:
            print(f"Modifying boxes with indices: {self.idx}")
            for i in self.idx:
                if i < len(self.bbox):
                    print(f"Original box {i}: {self.bbox[i]}")
                    new_coords = input(f"Enter new coordinates for box {i} (x1 y1 x2 y2, or press Enter to keep): ").strip()
                    cls = int(self.bbox[i][0])
                    if new_coords:
                        coords = new_coords.split()
                        if len(coords) == 4:
                            converted = self.convert(width, height, coords)
                            if converted:
                                newbbox.append([cls, *converted])
                                print(f"Updated box {i}: [cls={cls}, {converted}]")
                        else:
                            print("Invalid input format, keeping original")
                            newbbox.append(self.bbox[i])
                    else:
                        newbbox.append(self.bbox[i])
                else:
                    print(f"Index {i} is out of range, skipping")
        else:
            for i, box in enumerate(self.bbox):
                cls = int(box[0])
                newbbox.append([cls, *box[1:]])

        print("New bounding boxes:")
        for box in newbbox:
            print(box)
        
        try:
            with open('./refined/train/labels/' + self.imgName + '.txt', 'w') as f:
                for box in newbbox:
                    f.write(" ".join(map(str, box)) + '\n')
            print("SAVED!!!")
            logging.info(f"Modified and saved labels for {self.imgName}")
        except Exception as e:
            print(f"Error saving file: {e}")
            logging.error(f"Save error: {e}")

    def remove(self):
        imgPath = './refined/train/images/' + self.imgName + '.jpeg'
        txtPath = './refined/train/labels/' + self.imgName + '.txt'

        try:
            if os.path.exists(imgPath):
                os.remove(imgPath)
                print(f"Removed image file: {imgPath}")
                logging.info(f"Removed image file: {imgPath}")
            else:
                raise FileNotFoundError(f"Image file does not exist: {imgPath}")
        except Exception as e:
            print(f"Error removing image: {e}")
            logging.error(f"Remove image error: {e}")

        try:
            if os.path.exists(txtPath):
                os.remove(txtPath)
                print(f"Removed label file: {txtPath}")
                logging.info(f"Removed label file: {txtPath}")
            else:
                raise FileNotFoundError(f"Label file does not exist: {txtPath}")
        except Exception as e:
            print(f"Error removing label: {e}")
            logging.error(f"Remove label error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-img', '--imgName', type=str, help='image name')
    parser.add_argument('-o', '--object', type=str, default=None, help='object name')
    parser.add_argument('-n', '--numbering', nargs="+", type=str, default=[], help='image number')
    parser.add_argument('-id', '--label_index', nargs="+", type=int, default=[], help='label index ex) 1 2')
    parser.add_argument('-m', '--mode', type=str, default='check', help='modify label')
    args = parser.parse_args()

    imgName = args.imgName + '_' + args.object + '_' + args.numbering[0] + '_crop_' + args.numbering[1]
    
    refine = REFINE(imgName, args.label_index)
    if args.mode == 'check':
        refine.draw() 
    elif args.mode == 'modify':
        refine.modify()
    elif args.mode == 'remove':
        refine.remove()