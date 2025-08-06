import logging
import yaml
import torch
from torch.utils.data import DataLoader
import pathlib
from .custom_dataset import ConstructionProgressDataset
import torch.nn as nn
import torch.optim as optim
from ultralytics import YOLO
import numpy as np
from pathlib import Path

def custom_collate_fn(batch):
    """Custom collate function to handle variable-length bounding boxes"""
    images, bboxes_list, progress_list = zip(*batch)
    
    # Stack images (they should all be the same size now)
    images = torch.stack(images, 0)
    
    # Stack progress values
    progress = torch.stack(progress_list, 0)
    
    # For bboxes, we'll return them as a list since they have variable lengths
    # In a real YOLO implementation, you'd need to pad or handle this differently
    bboxes = list(bboxes_list)
    
    return images, bboxes, progress

class ProgressYOLO(nn.Module):
    """Custom YOLO model with progress regression head"""
    def __init__(self, base_model, progress_nc=1):
        super().__init__()
        self.base_model = base_model
        # Get the backbone output channels (typically from the last backbone layer)
        # For YOLOv8n, this is usually 512 channels before the neck
        backbone_channels = 512  # This may need adjustment based on model
        
        self.progress_head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(backbone_channels, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, progress_nc),
            nn.Sigmoid()
        )

    def forward(self, x):
        # Get YOLO detection outputs
        detection_outputs = self.base_model(x)
        
        # Extract features for progress prediction
        # We need to hook into the backbone features
        features = self._extract_backbone_features(x)
        progress = self.progress_head(features)
        
        return detection_outputs, progress
    
    def _extract_backbone_features(self, x):
        """Extract features from the backbone for progress prediction"""
        # This is a simplified approach - we'll use the model's backbone
        # In practice, you might need to modify this based on the exact YOLO architecture
        with torch.no_grad():
            # Get intermediate features from the backbone
            features = self.base_model.model[0](x)  # Backbone only
            if isinstance(features, (list, tuple)):
                features = features[-1]  # Take the last feature map
        return features

class CustomTrainer:
    """Custom trainer for YOLO + Progress regression"""
    
    def __init__(self, model, device, progress_weight=1.0):
        self.model = model
        self.device = device
        self.progress_weight = progress_weight
        self.mse_loss = nn.MSELoss()
        
    def train_epoch(self, dataloader, optimizer, epoch):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        total_detection_loss = 0.0
        total_progress_loss = 0.0
        
        for batch_idx, (images, labels, progress) in enumerate(dataloader):
            images = images.to(self.device)
            progress = progress.to(self.device).float()
            
            optimizer.zero_grad()
            
            try:
                # Forward pass
                detection_outputs, progress_pred = self.model(images)
                
                # Calculate progress loss
                progress_loss = self.mse_loss(progress_pred.squeeze(), progress)
                
                # For detection loss, we need to use YOLO's built-in loss calculation
                # This is simplified - in practice, you'd need proper YOLO loss calculation
                detection_loss = torch.tensor(0.0, device=self.device)
                
                # Combined loss
                total_batch_loss = detection_loss + self.progress_weight * progress_loss
                
                total_batch_loss.backward()
                optimizer.step()
                
                total_loss += total_batch_loss.item()
                total_detection_loss += detection_loss.item()
                total_progress_loss += progress_loss.item()
                
                if batch_idx % 10 == 0:
                    logging.info(f'Epoch {epoch}, Batch {batch_idx}/{len(dataloader)}, '
                               f'Loss: {total_batch_loss.item():.4f}, '
                               f'Progress Loss: {progress_loss.item():.4f}')
                    
            except Exception as e:
                logging.error(f"Error in batch {batch_idx}: {e}")
                continue
        
        avg_loss = total_loss / len(dataloader)
        avg_detection_loss = total_detection_loss / len(dataloader)
        avg_progress_loss = total_progress_loss / len(dataloader)
        
        return avg_loss, avg_detection_loss, avg_progress_loss

def create_simple_model(num_classes=1):
    """Create a simplified model for progress prediction only"""
    return nn.Sequential(
        nn.Conv2d(3, 32, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, 3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, num_classes),
        nn.Sigmoid()
    )

def main(config_path: str = "configs/training.yaml") -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    device = torch.device(f"cuda:{config['device']}" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")

    # Load data configuration
    try:
        with open(config['data'], 'r') as f:
            data_cfg = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Data config file {config['data']} not found")
        return

    # Setup dataset paths
    train_images_dir = pathlib.Path(data_cfg['train']).parent / "images"
    train_labels_dir = pathlib.Path(data_cfg['train']).parent / "labels"
    
    logging.info(f"Train images dir: {train_images_dir}")
    logging.info(f"Train labels dir: {train_labels_dir}")

    # Create dataset and dataloader
    try:
        dataset = ConstructionProgressDataset(train_images_dir, train_labels_dir, transform=None, img_size=config.get('imgsz', 640))
        dataloader = DataLoader(dataset, batch_size=config['batch'], shuffle=True, num_workers=0, collate_fn=custom_collate_fn)  # Set to 0 to avoid multiprocessing issues
        logging.info(f"Dataset loaded with {len(dataset)} samples")
    except Exception as e:
        logging.error(f"Error creating dataset: {e}")
        return

    # Create model - using simplified approach for now
    try:
        # Option 1: Use simplified progress-only model
        model = create_simple_model(num_classes=1).to(device)
        logging.info("Using simplified progress prediction model")
        
        # Option 2: Try to load YOLO model (commented out for now due to complexity)
        # base_model = YOLO('yolov8n.pt')
        # model = ProgressYOLO(base_model.model).to(device)
        
    except Exception as e:
        logging.error(f"Error creating model: {e}")
        return

    # Setup optimizer
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()

    epochs = config['epochs']
    logging.info(f"Starting training for {epochs} epochs")

    # Training loop for simplified model
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for batch_idx, (images, labels, progress) in enumerate(dataloader):
            images = images.to(device)
            progress = progress.to(device).float()

            optimizer.zero_grad()

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs.squeeze(), progress)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            if batch_idx % 10 == 0:
                logging.info(f'Epoch {epoch+1}/{epochs}, Batch {batch_idx}/{len(dataloader)}, '
                           f'Loss: {loss.item():.4f}')

        avg_loss = running_loss / len(dataloader)
        logging.info(f"Epoch {epoch+1}/{epochs} completed, Average Loss: {avg_loss:.4f}")

    # Save model
    save_path = config['save_path']
    torch.save(model.state_dict(), save_path)
    logging.info(f"Model trained and saved to {save_path}")

if __name__ == "__main__":
    main()
