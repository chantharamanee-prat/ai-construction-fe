import logging
import yaml
import torch
from torch.utils.data import DataLoader
from ultralytics import YOLO
import pathlib
from custom_dataset import ConstructionProgressDataset
import torch.nn as nn
import torch.optim as optim

class YOLOWithProgress(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.base_model = base_model
        # Add a regression head for progress percentage (single output)
        self.progress_head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(1280, 1),  # Assuming base_model outputs 1280 channels feature map
            nn.Sigmoid()  # Output between 0 and 1
        )

    def forward(self, x):
        # Forward through base YOLO model backbone to get features
        features = self.base_model.model.model[0](x)  # Access backbone (may need adjustment)
        # Forward through detection head (YOLO original)
        detection_output = self.base_model(x)
        # Forward through progress head
        progress_output = self.progress_head(features)
        return detection_output, progress_output

def main(config_path: str = "configs/training.yaml") -> None:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    device = torch.device(f"cuda:{config['device']}" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")

    # Load dataset
    data_cfg = yaml.safe_load(open(config['data']))
    train_images_dir = pathlib.Path(data_cfg['train']).parent / "images"
    train_labels_dir = pathlib.Path(data_cfg['train']).parent / "labels"

    dataset = ConstructionProgressDataset(train_images_dir, train_labels_dir, transform=None)
    dataloader = DataLoader(dataset, batch_size=config['batch'], shuffle=True)

    # Load base YOLO model
    base_model = YOLO(config['model_path']).to(device)
    model = YOLOWithProgress(base_model).to(device)

    criterion_detection = nn.CrossEntropyLoss()  # Placeholder, actual YOLO loss is complex
    criterion_progress = nn.MSELoss()

    optimizer = optim.Adam(model.parameters(), lr=1e-4)

    epochs = config['epochs']

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for imgs, bboxes, progress in dataloader:
            imgs = imgs.to(device)
            progress = progress.to(device)

            optimizer.zero_grad()

            detection_output, progress_output = model(imgs)

            # Calculate losses (simplified)
            loss_detection = criterion_detection(detection_output, bboxes)  # Placeholder
            loss_progress = criterion_progress(progress_output.squeeze(), progress.squeeze())

            loss = loss_detection + loss_progress
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        logging.info(f"Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(dataloader)}")

    torch.save(model.state_dict(), config['save_path'])
    logging.info(f"Model trained and saved to {config['save_path']}")

if __name__ == "__main__":
    main()
