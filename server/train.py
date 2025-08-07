import logging
import yaml
import torch
from torch.utils.data import DataLoader
import pathlib
from custom_dataset import ConstructionProgressDataset
import torch.nn as nn
import torch.optim as optim
from ultralytics import YOLO
import numpy as np
from pathlib import Path

from torchvision import transforms

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize((640, 640)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

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
        nn.BatchNorm2d(32),  # Add batch normalization
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, 3, padding=1),
        nn.BatchNorm2d(128),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.5),  # Increase dropout
        nn.Linear(64, 32),  # Add intermediate layer
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(32, num_classes),
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
    
    # Add validation paths
    val_images_dir = pathlib.Path(data_cfg.get('val', data_cfg['train'])).parent / "images"
    val_labels_dir = pathlib.Path(data_cfg.get('val', data_cfg['train'])).parent / "labels"
    
    logging.info(f"Train images dir: {train_images_dir}")
    logging.info(f"Train labels dir: {train_labels_dir}")

    # Create datasets and dataloaders
    try:
        train_dataset = ConstructionProgressDataset(train_images_dir, train_labels_dir, transform=transform, img_size=config.get('imgsz', 640))
        val_dataset = ConstructionProgressDataset(val_images_dir, val_labels_dir, transform=transform, img_size=config.get('imgsz', 640))
        
        train_dataloader = DataLoader(train_dataset, batch_size=config['batch'], shuffle=True, num_workers=0, collate_fn=custom_collate_fn)
        val_dataloader = DataLoader(val_dataset, batch_size=config['batch'], shuffle=False, num_workers=0, collate_fn=custom_collate_fn)
        
        logging.info(f"Train dataset: {len(train_dataset)} samples")
        logging.info(f"Val dataset: {len(val_dataset)} samples")
    except Exception as e:
        logging.error(f"Error creating dataset: {e}")
        return

    # Create model
    try:
        model = create_simple_model(num_classes=1).to(device)
        logging.info("Using simplified progress prediction model")
    except Exception as e:
        logging.error(f"Error creating model: {e}")
        return

    # Setup optimizer with improved parameters
    optimizer = optim.AdamW(model.parameters(), 
                           lr=float(config.get('learning_rate', 0.001)),
                           weight_decay=float(config.get('weight_decay', 1e-4)))
    
    # Add learning rate scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config['epochs'])
    
    criterion = nn.MSELoss()

    epochs = config['epochs']
    best_val_loss = float('inf')
    patience = config.get('early_stopping_patience', 20)
    patience_counter = 0
    
    logging.info(f"Starting training for {epochs} epochs")

    # Training loop with validation
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        
        for batch_idx, (images, labels, progress) in enumerate(train_dataloader):
            images = images.to(device)
            progress = progress.to(device).float()

            optimizer.zero_grad()

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs.squeeze(), progress)

            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()

            train_loss += loss.item()

            if batch_idx % 10 == 0:
                logging.info(f'Epoch {epoch+1}/{epochs}, Batch {batch_idx}/{len(train_dataloader)}, '
                           f'Loss: {loss.item():.4f}, LR: {optimizer.param_groups[0]["lr"]:.6f}')

        # Validation phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, labels, progress in val_dataloader:
                images = images.to(device)
                progress = progress.to(device).float()
                
                outputs = model(images)
                loss = criterion(outputs.squeeze(), progress)
                val_loss += loss.item()

        avg_train_loss = train_loss / len(train_dataloader)
        avg_val_loss = val_loss / len(val_dataloader)
        
        scheduler.step()
        
        logging.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

        # Early stopping
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), config['save_path'])
            logging.info(f"New best model saved with val loss: {avg_val_loss:.4f}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logging.info(f"Early stopping triggered after {epoch+1} epochs")
                break

    logging.info(f"Training completed. Best validation loss: {best_val_loss:.4f}")

if __name__ == "__main__":
    main()
