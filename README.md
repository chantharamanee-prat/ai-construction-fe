# AI Construction Progress Monitoring System

A full-stack application for monitoring construction site progress using AI-powered image analysis. The system allows users to annotate construction site images, train ML models on annotated data, and predict construction progress using trained YOLO-based models.

## Features

- **Image Annotation**: Interactive tool for annotating construction site images with bounding boxes
- **ML Training**: Train custom YOLO models for progress classification and object detection
- **Progress Prediction**: Analyze new construction images to estimate completion progress
- **Dataset Management**: Organize datasets by progress percentage for supervised learning

## Tech Stack

### Backend
- **Python 3.11** with FastAPI for REST API
- **Ultralytics YOLO** for object detection and classification
- **PyTorch** for ML model training
- **Uvicorn/Gunicorn** for ASGI server deployment

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling
- **React Router** for client-side routing
- **React Konva** for interactive image annotation
- **Axios** for API communication

### Deployment
- **Docker** with Docker Compose
- **Nginx** for production serving
- **Jenkins** for CI/CD pipeline

## Prerequisites

- **Python 3.11+** - Download from [python.org](https://www.python.org/downloads/)
- **Node.js 18+** and npm - Download from [nodejs.org](https://nodejs.org/)
- **Git** - For version control
- (Optional) **Docker** and **Docker Compose** - For containerized deployment

## Project Structure

```
ai-construction-fe/
├── server/                    # Backend FastAPI application
│   ├── api.py                # Main FastAPI app
│   ├── api_handlers/         # API endpoint handlers
│   ├── ml_scripts/          # ML models and training scripts
│   ├── datasets/            # Training and inference data
│   │   ├── raw_images/      # Original images organized by progress %
│   │   └── labels/          # YOLO format annotations
│   ├── configs/             # Training configuration files
│   ├── train.py            # Model training script
│   └── split_dataset.py    # Dataset splitting utility
├── web/                      # Frontend React application
│   ├── src/
│   │   ├── api/            # API client services
│   │   └── components/     # React components
│   └── package.json
├── requirements.txt           # Python dependencies
├── docker-compose.yml        # Docker orchestration
├── Dockerfile               # Backend Docker image
└── README.md               # This file
```

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-construction-fe
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Verify ML Models

Make sure the following model files exist in the server directory:
- `server/ml_scripts/classification/models/progress-classification.pt`
- `server/ml_scripts/detection/models/progress-detection.pt`

If models are missing, you'll need to train them using the training scripts.

#### Start Backend Development Server

```bash
# Using the provided script (recommended)
./start-server.sh

# Or directly with uvicorn
cd server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd web
npm install
```

#### Start Frontend Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Access the Application

Open your browser and navigate to `http://localhost:5173`

- **Dataset List**: Browse and select construction datasets
- **Annotation Tool**: Annotate images with bounding boxes for training
- **ML Prediction**: Upload images for progress analysis

## API Endpoints

### Health Check
- `GET /health` - Check if the API is running

### Dataset Management
- `GET /api/datasets` - List all available datasets
- `GET /api/datasets/{dataset_name}` - Get images and annotations for a specific dataset
- `GET /api/images/{image_path}` - Serve image files

### Annotation
- `POST /api/annotations` - Save annotation data

### ML Prediction
- `POST /api/predict` - Run ML inference on uploaded image
  - Returns: Progress percentage + detected objects with confidence scores

## ML Model Training

### Prepare Dataset

Organize your images in `server/datasets/raw_images/{progress_percentage}/`:
```
datasets/raw_images/
├── 10%/
│   ├── image1.jpg
│   ├── image2.jpg
└── 20%/
    ├── image3.jpg
    └── image4.jpg
```

### Train Classification Model

```bash
cd server
python train.py
```

Training configuration: `server/configs/training.yaml`

### Split Dataset for Training

```bash
cd server
python split_dataset.py
```

This splits images into train/val/test sets based on `server/configs/dataset.yaml`

## Development Commands

### Backend

```bash
# Development mode
./start-server.sh

# Production mode
./start-production.sh

# Manual start with uvicorn
cd server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd web

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Preview production build
npm run preview
```

## Docker Deployment

### Build Docker Images

```bash
# Build backend API image
docker build -t yolo-server-api -f Dockerfile .

# Build frontend web image
docker build -t yolo-server-web -f web/Dockerfile web/
```

### Run with Docker Compose

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart services
docker compose restart
```

Services:
- **Backend API**: `http://localhost:9500` (maps to container port 8000)
- **Frontend**: `http://localhost:9501` (maps to container port 80)

## Annotation Format

Annotations are saved in YOLO format with one bounding box per line:
```
class_id x_center y_center width height
```

Where:
- `class_id`: Integer class identifier (0-5)
- `x_center`, `y_center`: Normalized coordinates (0.0-1.0)
- `width`, `height`: Normalized dimensions (0.0-1.0)

## ML Models

### Classification Model
- **Location**: `server/ml_scripts/classification/models/progress-classification.pt`
- **Purpose**: Predict overall construction progress percentage
- **Classes**: 10%, 15%, 20%, 25%, 30%, 40%, 50%
- **Output**: Top 5 predictions with confidence scores

### Detection Model
- **Location**: `server/ml_scripts/detection/models/progress-detection.pt`
- **Purpose**: Detect construction elements
- **Classes**: foundation, column, beam, roof, wall, floor
- **Output**: Bounding boxes with class names and confidence scores

## Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed
- Activate the virtual environment
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify that port 8000 is not already in use

### Frontend won't start
- Ensure Node.js 18+ is installed
- Install dependencies: `npm install`
- Check that port 5173 is not already in use

### ML Prediction fails
- Ensure model files exist at the expected paths
- Verify that the image format is supported (jpg, png, etc.)
- Check backend logs for specific error messages

### Dataset issues
- Ensure images are organized in `server/datasets/raw_images/{progress_percentage}/`
- Verify that folder names are valid percentage values (e.g., "10%", "15%")
- Check file permissions on dataset directories

## CI/CD Pipeline

The project includes a Jenkins pipeline (`Jenkinsfile`) that:

1. Triggers on commits to the `master` branch
2. Builds Docker images for frontend and backend
3. Restarts containers using Docker Compose
4. Skips build/deploy on other branches

## Environment Variables

### Backend
- `PYTHONUNBUFFERED=1` - Ensure Python output is not buffered
- `PYTHONPATH=/app` - Set Python path for imports

### Frontend
- `VITE_BASE_API` - Backend API base URL (default: http://localhost:8000)
- Configure in `web/.env.production` for production builds

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions, please open an issue on the project repository.

---

**Happy coding!** 🚧🏗️