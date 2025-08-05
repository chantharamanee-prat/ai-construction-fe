# System Patterns

## System architecture
Monolithic

## Key technical decisions
- Using YOLOv8 for object detection
- Python-based implementation
- Ultralytics framework
- Extended YOLOv8 model with regression head for construction progress prediction
- Custom dataset loader for multi-task learning (detection + progress regression)
- Custom training loop integrating detection and regression losses

## Design patterns and best practices
- Configuration management using external YAML files for annotation, dataset splitting, and training parameters
- Error handling with logging for robust operation and debugging
- Logging standards set to DEBUG level for detailed traceability
- Use of pathlib for path management to improve cross-platform compatibility
- Modular code organization separating annotation, data processing, and training into distinct modules
- Adoption of type hints and docstrings for improved code readability and maintainability

## Critical implementation paths
1. Data preprocessing pipeline
2. Model training configuration
3. Inference API
