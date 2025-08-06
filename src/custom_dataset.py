import pathlib
import torch
from torch.utils.data import Dataset
import cv2
import numpy as np
from torchvision import transforms

class ConstructionProgressDataset(Dataset):
    def __init__(self, images_dir: pathlib.Path, labels_dir: pathlib.Path, transform=None, img_size=640):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.img_size = img_size
        self.image_paths = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
        
        # Default transform if none provided
        if transform is None:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((img_size, img_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        img = cv2.imread(str(img_path))
        
        if img is None:
            # Handle corrupted images
            print(f"Warning: Could not load image {img_path}")
            img = np.zeros((self.img_size, self.img_size, 3), dtype=np.uint8)
        else:
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
                        progress_str = line.split(":")[1].strip()
                        # Handle percentage format (e.g., "10%" -> 0.1)
                        if progress_str.endswith('%'):
                            progress = float(progress_str[:-1]) / 100.0
                        else:
                            progress = float(progress_str)
                    except (ValueError, IndexError):
                        progress = None
                elif line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) == 5:
                        try:
                            class_id = int(parts[0])
                            bbox = list(map(float, parts[1:]))
                            bboxes.append([class_id] + bbox)
                        except ValueError:
                            continue

        # Convert to tensors
        bboxes = torch.tensor(bboxes, dtype=torch.float32) if bboxes else torch.zeros((0, 5), dtype=torch.float32)
        progress = torch.tensor(progress, dtype=torch.float32) if progress is not None else torch.tensor(-1.0, dtype=torch.float32)

        # Apply transforms to image
        if self.transform:
            img = self.transform(img)

        return img, bboxes, progress
