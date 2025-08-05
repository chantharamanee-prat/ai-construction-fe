from ultralytics import YOLO
import torch

def main():
    print(f"CUDA available: {torch.cuda.is_available()}")

    # Load pretrained YOLOv8n model
    model = YOLO("models/yolov8n.pt")

    # Train the model
    results = model.train(
        data="data.yaml",
        epochs=100,
        imgsz=640,
        batch=16,
        device=0  # Use GPU device 0
    )

    # Export the best model to ONNX format
    model.export(format="onnx")

    # Save the trained model weights
    model.save("models/construction_progress.pt")

if __name__ == "__main__":
    main()
