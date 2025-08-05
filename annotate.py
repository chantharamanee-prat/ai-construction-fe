import cv2
import os
import json

class Annotator:
    def __init__(self, image_dir, output_dir, classes):
        self.image_dir = image_dir
        self.output_dir = output_dir
        self.classes = classes
        self.images = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        self.index = 0
        self.current_image = None
        self.bboxes = []  # list of (class_id, x_center, y_center, width, height) normalized
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.window_name = "Annotator"
        os.makedirs(output_dir, exist_ok=True)

    def draw_bbox(self, img, bbox, color=(0, 255, 0)):
        h, w = img.shape[:2]
        class_id, x_c, y_c, bw, bh = bbox
        x1 = int((x_c - bw / 2) * w)
        y1 = int((y_c - bh / 2) * h)
        x2 = int((x_c + bw / 2) * w)
        y2 = int((y_c + bh / 2) * h)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = self.classes[class_id]
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.current_image_copy = self.current_image.copy()
                cv2.rectangle(self.current_image_copy, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
                cv2.imshow(self.window_name, self.current_image_copy)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            x1, y1 = self.ix, self.iy
            x2, y2 = x, y
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            h, w = self.current_image.shape[:2]
            x_c = ((x1 + x2) / 2) / w
            y_c = ((y1 + y2) / 2) / h
            bw = (x2 - x1) / w
            bh = (y2 - y1) / h
            print("Select class for bounding box:")
            for i, cls in enumerate(self.classes):
                print(f"{i}: {cls}")
            while True:
                class_id_str = input("Enter class id: ")
                if class_id_str.isdigit() and 0 <= int(class_id_str) < len(self.classes):
                    class_id = int(class_id_str)
                    break
                else:
                    print("Invalid class id. Try again.")
            self.bboxes.append((class_id, x_c, y_c, bw, bh))
            self.draw_bbox(self.current_image, self.bboxes[-1])
            cv2.imshow(self.window_name, self.current_image)

    def save_annotations(self):
        base_name = os.path.splitext(self.images[self.index])[0]
        label_path = os.path.join(self.output_dir, base_name + ".txt")
        with open(label_path, "w") as f:
            for bbox in self.bboxes:
                f.write(" ".join(map(str, bbox)) + "\n")

    def run(self):
        while self.index < len(self.images):
            img_path = os.path.join(self.image_dir, self.images[self.index])
            self.current_image = cv2.imread(img_path)
            if self.current_image is None:
                print(f"Failed to load {img_path}")
                self.index += 1
                continue
            self.bboxes = []
            self.current_image_copy = self.current_image.copy()
            cv2.namedWindow(self.window_name)
            cv2.setMouseCallback(self.window_name, self.mouse_callback)
            print(f"Annotating image {self.index + 1}/{len(self.images)}: {self.images[self.index]}")
            cv2.imshow(self.window_name, self.current_image)
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('n'):  # Next image
                    self.save_annotations()
                    self.index += 1
                    break
                elif key == ord('q'):  # Quit
                    self.save_annotations()
                    cv2.destroyAllWindows()
                    return
                elif key == ord('d'):  # Delete last bbox
                    if self.bboxes:
                        self.bboxes.pop()
                        self.current_image = cv2.imread(img_path)
                        for bbox in self.bboxes:
                            self.draw_bbox(self.current_image, bbox)
                        cv2.imshow(self.window_name, self.current_image)
            cv2.destroyAllWindows()

if __name__ == "__main__":
    classes = ['foundation', 'column', 'beam', 'roof', 'wall']
    image_dir = "datasets/raw_images"
    output_dir = "datasets/labels"
    annotator = Annotator(image_dir, output_dir, classes)
    annotator.run()
