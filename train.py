import logging
import yaml
from ultralytics import YOLO
import torch

def main(config_path: str = "configs/training.yaml") -> None:
    """
    Train YOLO model based on configuration.

    Args:
        config_path (str): Path to YAML configuration file.
    """
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    logging.info(f"CUDA available: {torch.cuda.is_available()}")

    model = YOLO(config['model_path'])

    results = model.train(
        data=config['data'],
        epochs=config['epochs'],
        imgsz=config['imgsz'],
        batch=config['batch'],
        device=config['device']
    )

    model.export(format=config['export_format'])
    model.save(config['save_path'])
    logging.info(f"Model trained and saved to {config['save_path']}")

if __name__ == "__main__":
    main()
