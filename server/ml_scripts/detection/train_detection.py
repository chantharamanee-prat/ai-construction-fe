from ultralytics import YOLO

model = YOLO("../../models/yolo11n.pt")  # load a pretrained model (recommended for training)


# Train the model
results = model.train(data="../../datasets/detection.yaml", epochs=100, imgsz=640)

best_model = YOLO(results.save_dir / "weights" / "best.pt")
best_model.save("models/progress-detection.pt")