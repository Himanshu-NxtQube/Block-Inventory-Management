import cv2
from ultralytics import YOLO
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

class BoxUtilities:
    def __init__(self):
        self.box_model = YOLO('models/block_box_latesssssssssstttttt.pt')
        self.stack_count_csv = pd.read_csv('inventory data/block_main_csv.csv', index_col='Part number')
        self.stack_count_csv = self.stack_count_csv[~self.stack_count_csv.index.duplicated(keep='first')]
        self.sticker_model = YOLO('models/block_sticker.pt')

    def get_stack_count(self, record, area):
        if not record:
            return None
        
        if not area:
            return -1
        
        print("Area:",area)
        exceptions = ['1203ES200181N', '1203ES200211N', '1203ES200201N', '1203ES200191N', '609AAA00821N', '1803AS200471N','2301ES200791N','2301AS207141N','1106AAA02641N','2301AS207151N','2301AS207141N','2301AS207131N','1106AAA02641A','2301ES200791N','1106AAA02641A','101EW503850N','203AAR16871N','101EW504250N','1805AAA01291N']
        # for record in records:
        part_number = record['part_number']
        if part_number[0] == '0':
            part_number = part_number[1:]
        if part_number in exceptions:
            print("Found exception", record['part_number'])
            return 1
        else:
            if part_number == '':
                return -2
            elif part_number not in self.stack_count_csv.index:
                print(f"Part number {part_number} not found in stack csv")
                return -3

            range1 = self.stack_count_csv.loc[part_number]['S1 Area final range']
            print("Range1",range1)
            if not pd.isna(range1):
                s1, e1 = range1.split('-')
                s1 = int(s1)
                e1 = int(e1)
            else:
                # print("Range 1 not found")
                # stack_counts.append(None)
                # continue
                s1, e1 = -1, -1

            range2 = self.stack_count_csv.loc[part_number]['S2 Area final range']
            print("Range2",range2)
            if not pd.isna(range2):
                s2, e2 = range2.split('-')
                s2 = int(s2)
                e2 = int(e2)
            else:
                # print("Range 2 not found")
                # stack_counts.append(None)
                # continue
                s2, e2 = -1, -1

            range3 = self.stack_count_csv.loc[part_number]['S3 Area final range']
            print("Range3",range3)
            if not pd.isna(range3):
                s3, e3 = range3.split('-')
                s3 = int(s3)
                e3 = int(e3)
            else:
                # print("Range 3 not found")
                # stack_counts.append(None)
                # continue
                s3, e3 = -1, -1

            if s1 < area < e1:
                return 1
            elif s2 < area < e2:
                return 2
            elif s3 < area < e3:
                return 3
            else:
                return None
    
    def get_nearest_box(self, image_path, image, rotation, debug=False):
        # image = cv2.imread(image_path)
        # if image is None:
        #     print(f"Error: Could not load {image_path}")
        #     return 0
        
        h, w, _ = image.shape
        center_point = (w // 2, h // 2)

        
        preds = self.box_model.predict(image, verbose=False)

        nearest_box = None
        min_distance = float('inf')

        for result in preds:
            boxes = result.obb.xyxyxyxy
            confs = result.obb.conf
            classes = result.obb.cls

            for corners, conf, cls in zip(boxes, confs, classes):
                pts = corners.cpu().numpy().astype(int).reshape((-1, 1, 2))
                
                # Calculate centroid of the bounding box
                M = cv2.moments(pts)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    continue  # skip invalid boxes

                # Calculate distance from image center to box center
                distance = np.sqrt((cx - center_point[0])**2 + (cy - center_point[1])**2)

                # Keep track of the nearest one
                if distance < min_distance:
                    min_distance = distance
                    nearest_box = pts

        if debug:
            # Draw all boxes, highlight the nearest one
            for result in preds:
                boxes = result.obb.xyxyxyxy
                for corners in boxes:
                    pts = corners.cpu().numpy().astype(int).reshape((-1, 1, 2))
                    color = (0, 255, 0) if np.array_equal(pts, nearest_box) else (0, 0, 255)
                    cv2.polylines(image, [pts], isClosed=True, color=color, thickness=5)

            # Convert and save image
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            os.makedirs("output", exist_ok=True)
            plt.imsave(f"output/{os.path.basename(image_path).split('.')[0]}_{rotation}.JPG", image_rgb)
        
        return nearest_box
    
    def crop_rotated_box(self, image_path, image, box_pts):
        # box_pts → (4,1,2) → convert to (4,2)
        pts = box_pts.reshape(4, 2).astype("float32")

        # Order points (optional but safer)
        # Find top-left, top-right, bottom-right, bottom-left
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]   # top-left
        rect[2] = pts[np.argmax(s)]   # bottom-right

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # top-right
        rect[3] = pts[np.argmax(diff)]  # bottom-left

        (tl, tr, br, bl) = rect

        # Compute width and height
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = int(max(widthA, widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = int(max(heightA, heightB))

        # Destination points for warp
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        # Compute perspective transform
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        cv2.imwrite(f'output/cropped_box_{os.path.basename(image_path).split(".")[0]}.jpg', warped)

        return warped

            
    def calculate_area(self, pts: np.ndarray) -> float:
        """Calculate area of a polygon from its corner points."""
        pts = np.array(pts, dtype=np.float32).reshape((-1, 1, 2))
        area = cv2.contourArea(pts)
        return float(area)
    
    def find_unique_id(self, unique_ids, nearest_box):
        if nearest_box is None:
            return None
        for unique_id, (x, y) in unique_ids:
            result = cv2.pointPolygonTest(nearest_box, (x, y), False)
            if result >= 0:
                return unique_id

    # def count(self, nearest_box):
    #     area_of_nearest = self.calculate_area(nearest_box)
    #     return area_of_nearest

    def check_unique_id_count(self, image, nearest_box, matching_unique_id):
        preds = self.sticker_model.predict(image, verbose=False)
        sticker_count = 0

        for result in preds:
            boxes = result.obb.xyxyxyxy
            confs = result.obb.conf
            classes = result.obb.cls

            for corners, conf, cls in zip(boxes, confs, classes):
                pts = corners.cpu().numpy().astype(int).reshape((-1, 1, 2))
                
                # Calculate centroid of the bounding box
                M = cv2.moments(pts)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                else:
                    continue  # skip invalid boxes

                result = cv2.pointPolygonTest(nearest_box, (cx, cy), False)
                if result >= 0:
                    sticker_count += 1
        
        for result in preds:
            boxes = result.obb.xyxyxyxy
            for corners in boxes:
                pts = corners.cpu().numpy().astype(int).reshape((-1, 1, 2))
                color = (0, 255, 0) if np.array_equal(pts, nearest_box) else (0, 0, 255)
                cv2.polylines(image, [pts], isClosed=True, color=color, thickness=5)

        return sticker_count
        


if __name__ == '__main__':
    bu = BoxUtilities()
    _dir = r'testing images/debug2'
    os.makedirs('output', exist_ok=True)
    with open('results3.csv', 'w') as f:
        for imagename in os.listdir(_dir):
            imagepath = os.path.join(_dir, imagename)
            image = cv2.imread(imagepath)
            nearest_box = bu.get_nearest_box(imagepath, image)
            area = bu.calculate_area(nearest_box)
            f.write(f"{imagename},{area}\n")
