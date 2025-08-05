import pathlib
import torch
from torch.utils.data import Dataset
import cv2

class ConstructionProgressDataset(Dataset):
    def __init__(self, images_dir: pathlib.Path, labels_dir: pathlib.Path, transform=None):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.transform = transform
        self.image_paths = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        label_path = self.labels_dir / (img_path.stem + ".txt")
        bboxes = []
        progress = None

        if label_path.exists():
            with open(label_path, 'r') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("# progress:"):
                    try:
                        progress = float(line.split(":")[1].strip())
                    except ValueError:
                        progress = None
                elif line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        bbox = list(map(float, parts[1:]))
                        bboxes.append([class_id] + bbox)

        bboxes = torch.tensor(bboxes) if bboxes else torch.zeros((0, 5), dtype=torch.float32)
        progress = torch.tensor([progress], dtype=torch.float32) if progress is not None else torch.tensor([-1.0], dtype=torch.float32)

        if self.transform:
            img = self.transform(img)

        return img, bboxes, progress
