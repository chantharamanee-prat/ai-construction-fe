# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a construction progress monitoring system using AI-powered image analysis. The system consists of:

- **Backend**: Python FastAPI server for ML inference and dataset management
- **Frontend**: React/TypeSingle with Vite for image annotation and visualization
- **ML Models**: YOLO-based models for construction object detection and progress classification
- **Deployment**: Docker containers orchestrated via Docker Compose with Jenkins CI/CD

The system allows users to annotate construction site images, train ML models on the annotated data, and predict construction progress using trained models.

## Development Commands

### Frontend Development (React/TypeScript)

```bash
cd web
npm install                    # Install dependencies
npm run dev                   # Start development server (default: http://localhost:5173)
npm run build                 # Build for production
npm run lint                  # Run ESLint
npm run preview               # Preview production build
```

### Backend Development (Python/FastAPI)

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
./start-server.sh             # Development mode (uvicorn)

# Start production server
./start-production.sh         # Production mode (gunicorn + uvicorn workers)
```

The backend runs on port 8000 and serves:
- API endpoints for dataset management and ML inference
- Static images from `server/datasets/raw_images/`

### ML Model Training

```bash
cd server
python train.py               # Train progress classification model
```

Training configuration is in `server/configs/training.yaml` and dataset configuration in `server/configs/dataset.yaml`.

### Dataset Management

```bash
cd server
python split_dataset.py       # Split dataset into train/val/test sets
```

This script uses configuration from `server/configs/dataset.yaml` to split images and labels based on progress percentage classes.

### Docker Development

```bash
# Build images
docker build -t yolo-server-api -f Dockerfile .
docker build -t yolo-server-web -f web/Dockerfile web/

# Run containers
docker compose up -d           # Start all services
docker compose down            # Stop all services
docker compose logs -f         # View logs
```

Services:
- `yolo-server`: Backend API on port 9500 (container: 8000)
- `yolo-web`: Frontend on port 9501 (container: 80)

## Architecture

### Backend Structure

```
server/
├── api.py                    # Main FastAPI application
├── api_handlers/             # API endpoint handlers
│   ├── image_loader.py      # Dataset image serving
│   ├── annotation_handler.py # Annotation CRUD operations
│   └── ml_handler.py       # ML model inference
├── ml_scripts/              # ML training and inference
│   ├── classification/      # Progress classification models
│   └── detection/         # Object detection models
├── datasets/               # Training and inference data
│   ├── raw_images/         # Original dataset images organized by progress %
│   └── labels/            # YOLO-format annotation labels
├── dto/                    # Data transfer objects (Pydantic models)
├── configs/                # Training and dataset configuration
├── train.py               # Model training script
└── split_dataset.py        # Dataset splitting utility
```

### Frontend Structure

```
web/src/
├── api/                    # API client services
│   ├── annotationService.ts # Dataset and annotation APIs
│   └── predictionService.ts # ML prediction APIs
├── components/             # React components
│   ├── DatasetList/       # Dataset browsing page
│   ├── AnnotationTool/     # Image annotation interface
│   └── MLPredictPage.tsx # ML inference interface
└── App.tsx                # Main application with routing
```

### Key API Endpoints

**Backend API (port 8000):**
- `GET /health` - Health check
- `GET /api/datasets` - List all datasets (folders in raw_images/)
- `GET /api/datasets/{dataset_name}` - Get images and annotations for a dataset
- `GET /api/images/{image_path:path}` - Serve image files
- `POST /api/annotations` - Save annotation data
- `POST /api/predict` - Run ML inference on uploaded image

**Frontend Development Server (port 5173):**
- `/` - Dataset list page
- `/annotate/:datasetName/:index` - Annotation tool
- `/ml-predict` - ML prediction page

### ML Models

**Classification Model (`ml_scripts/classification/models/progress-classification.pt`):**
- Predicts overall construction progress percentage (10%, 15%, 20%, 25%, 30%, 40%, 50%)
- Returns top 5 predictions with confidence scores

**Detection Model (`ml_scripts/detection/models/progress-detection.pt`):**
- Detects construction elements (foundation, column, beam, roof, wall, floor)
- Returns bounding boxes with class names and confidence scores

Both models use the Ultralytics YOLO framework.

### Data Flow

1. **Annotation Workflow**:
   - User selects a dataset (organized by progress percentage)
   - Annotation tool loads images and displays existing annotations
   - User draws/modifies bounding boxes using react-konva canvas
   - Annotations saved as YOLO format (class_id x_center y_center width height) in `server/datasets/labels/`

2. **ML Training**:
   - Dataset split into train/val/test sets by `split_dataset.py`
   - Training script loads custom PyTorch dataset with data augmentation
   - Progress classification model trained with MSE loss and AdamW optimizer
   - Best model saved based on validation loss

3. **ML Inference**:
   - Frontend uploads image via `/api/predict`
   - Backend runs both classification and detection models
   - Returns combined results: progress percentage + detected objects

### Environment Variables

**Backend:**
- `VITE_BASE_API` - Backend API base URL (default: http://localhost:8000)

**Frontend:**
- Configure in `web/.env.production` for deployment

### CI/CD Pipeline

Jenkins pipeline (`Jenkinsfile`) automates deployment:
- Triggers on commits to master branch
- Builds Docker images for both frontend and backend
- Restarts containers using Docker Compose
- Only runs on master branch (other branches skip build/deploy)

## Important Notes

- Dataset organization: Images must be organized in `server/datasets/raw_images/{progress_percentage}/` where folder names are valid percentage values (e.g., "10%", "15%")
- Label format: YOLO format files with `.txt` extension, one line per box: `class_id x_center y_center width height`
- ML models must exist at expected paths before inference can work
- Frontend uses React Router for navigation between pages
- CORS is enabled for all origins on the backend API
- Production deployment uses Nginx to serve the built React frontend
