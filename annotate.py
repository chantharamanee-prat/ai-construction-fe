
import cv2
import pathlib
import logging
import yaml
from typing import List, Tuple

class Annotator:
    """
    Annotation tool for labeling images with bounding boxes and class IDs.

    Attributes:
        image_dir (pathlib.Path): Directory containing images to annotate.
        output_dir (pathlib.Path): Directory to save annotation files.
        classes (List[str]): List of class names.
        images (List[pathlib.Path]): List of image file paths.
        index (int): Current image index.
        current_image (cv2.Mat): Current image being annotated.
        bboxes (List[Tuple[int, float, float, float, float]]): List of bounding boxes.
        drawing (bool): Flag indicating if drawing is in progress.
        ix (int): Initial x-coordinate of bounding box.
        iy (int): Initial y-coordinate of bounding box.
        window_name (str): Name of the OpenCV window.
    """

    def __init__(self, config_path: str):
        """
        Initialize the Annotator with configuration from a YAML file.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.load_config(config_path)
        self.images = [p for p in self.image_dir.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
        self.index = 0
        self.current_image = None
        self.bboxes = []
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.window_name = "Annotator"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_config(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.image_dir = pathlib.Path(config['image_dir'])
        self.output_dir = pathlib.Path(config['output_dir'])
        self.classes = config['classes']

    def draw_bbox(self, img: cv2.Mat, bbox: Tuple[int, float, float, float, float], color: Tuple[int, int, int]=(0, 255, 0)) -> None:
        """Draw a bounding box on the image."""
        h, w = img.shape[:2]
        class_id, x_c, y_c, bw, bh = bbox
        x1 = int((x_c - bw / 2) * w)
        y1 = int((y_c - bh / 2) * h)
        x2 = int((x_c + bw / 2) * w)
        y2 = int((y_c + bh / 2) * h)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = self.classes[class_id]
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def mouse_callback(self, event: int, x: int, y: int, flags: int, param) -> None:
        """Handle mouse events for drawing bounding boxes."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
            logging.debug(f"Started drawing at ({x}, {y})")
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
            logging.debug(f"Finished drawing bbox: class_id pending selection, coords: ({x_c}, {y_c}, {bw}, {bh})")
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
            logging.debug(f"Added bbox with class_id {class_id}")

    def save_annotations(self) -> None:
        """Save annotations to a text file in YOLO format."""
        base_name = self.images[self.index].stem
        label_path = self.output_dir / f"{base_name}.txt"
        try:
            with open(label_path, "w") as f:
                for bbox in self.bboxes:
                    f.write(" ".join(map(str, bbox)) + "\n")
            logging.info(f"Saved annotations to {label_path}")
        except Exception as e:
            logging.error(f"Failed to save annotations: {e}")

    def run(self) -> None:
        """Run the annotation tool."""
        while self.index < len(self.images):
            img_path = self.images[self.index]
            self.current_image = cv2.imread(str(img_path))
            if self.current_image is None:
                logging.error(f"Failed to load {img_path}")
                self.index += 1
                continue
            self.bboxes = []
            self.current_image_copy = self.current_image.copy()
            cv2.namedWindow(self.window_name)
            cv2.setMouseCallback(self.window_name, self.mouse_callback)
            logging.info(f"Annotating image {self.index + 1}/{len(self.images)}: {img_path.name}")
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
                        self.current_image = cv2.imread(str(img_path))
                        for bbox in self.bboxes:
                            self.draw_bbox(self.current_image, bbox)
                        cv2.imshow(self.window_name, self.current_image)
            cv2.destroyAllWindows()

if __name__ == "__main__":
    annotator = Annotator("configs/annotation.yaml")
    annotator.run()
