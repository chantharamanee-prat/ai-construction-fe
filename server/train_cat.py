import torch
import torchvision.transforms as T

from ultralytics import YOLO
from ultralytics.data.dataset import ClassificationDataset
from ultralytics.models.yolo.classify import ClassificationTrainer, ClassificationValidator


class CustomizedDataset(ClassificationDataset):
    """A customized dataset class for image classification with enhanced data augmentation transforms."""

    def __init__(self, root: str, args, augment: bool = False, prefix: str = ""):
        """Initialize a customized classification dataset with enhanced data augmentation transforms."""
        super().__init__(root, args, augment, prefix)

        # Add your custom training transforms here
        train_transforms = T.Compose(
            [
                T.Resize((args.imgsz, args.imgsz)),
                T.RandomHorizontalFlip(p=args.fliplr),
                T.RandomVerticalFlip(p=args.flipud),
                T.RandAugment(interpolation=T.InterpolationMode.BILINEAR),
                T.ColorJitter(brightness=args.hsv_v, contrast=args.hsv_v, saturation=args.hsv_s, hue=args.hsv_h),
                T.ToTensor(),
                T.Normalize(mean=torch.tensor(0), std=torch.tensor(1)),
                T.RandomErasing(p=args.erasing, inplace=True),
            ]
        )

        # Add your custom validation transforms here
        val_transforms = T.Compose(
            [
                T.Resize((args.imgsz, args.imgsz)),
                T.ToTensor(),
                T.Normalize(mean=torch.tensor(0), std=torch.tensor(1)),
            ]
        )
        self.torch_transforms = train_transforms if augment else val_transforms


class CustomizedTrainer(ClassificationTrainer):
    """A customized trainer class for YOLO classification models with enhanced dataset handling."""

    def build_dataset(self, img_path: str, mode: str = "train", batch=None):
        """Build a customized dataset for classification training and the validation during training."""
        return CustomizedDataset(root=img_path, args=self.args, augment=mode == "train", prefix=mode)


class CustomizedValidator(ClassificationValidator):
    """A customized validator class for YOLO classification models with enhanced dataset handling."""

    def build_dataset(self, img_path: str, mode: str = "train"):
        """Build a customized dataset for classification standalone validation."""
        return CustomizedDataset(root=img_path, args=self.args, augment=mode == "train", prefix=self.args.split)
# Load a model
# model = YOLO("models/yolo11n-cls.yaml")  # build a new model from YAML
model = YOLO("models/yolo11n-cls.pt")  # load a pretrained model (recommended for training)
# model = YOLO("models/yolo11n-cls.yaml").load("models/yolo11n-cls.pt")  # build from YAML and transfer weights

# Train the model
results = model.train(data="datasets/split", trainer=CustomizedTrainer, epochs=100, imgsz=640)

model.save("test-cat.pt")