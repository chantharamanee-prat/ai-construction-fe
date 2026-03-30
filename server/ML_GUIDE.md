# ML Pipeline Guide for Non-Experts

This guide explains how the machine learning (ML) system works in plain language, walks through every step of the process, and gives practical tips for improving model accuracy.

---

## Table of Contents

1. [What Does This System Do?](#what-does-this-system-do)
2. [The Big Picture](#the-big-picture)
3. [Step-by-Step Walkthrough](#step-by-step-walkthrough)
4. [How the Code Works](#how-the-code-works)
5. [How to Make the Model More Accurate](#how-to-make-the-model-more-accurate)
6. [Quick Reference: File Map](#quick-reference-file-map)
7. [Troubleshooting](#troubleshooting)

---

## What Does This System Do?

The system uses **two AI models** to analyze photos of construction sites:

| Model | What It Does | Example Output |
|---|---|---|
| **Classification Model** | Estimates overall construction progress | "This site is 30% complete (92% confident)" |
| **Detection Model** | Identifies specific construction elements in the photo | Draws boxes around columns, beams, walls, etc. |

Think of it like this:
- The **classification model** is like a person looking at a site and saying "this looks about 30% done."
- The **detection model** is like a person pointing at specific things and saying "that's a column, that's a beam, that's a wall."

---

## The Big Picture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│ 1. Collect  │────▶│ 2. Annotate  │────▶│ 3. Split     │────▶│ 4. Train    │
│    Photos   │     │    (Label)   │     │    Dataset   │     │    Models   │
│             │     │              │     │              │     │             │
│ Put photos  │     │ Draw boxes   │     │ 80% train    │     │ AI learns   │
│ in folders  │     │ around       │     │ 20% validate │     │ patterns    │
│ by progress │     │ objects      │     │              │     │             │
└─────────────┘     └──────────────┘     └──────────────┘     └──────┬──────┘
                                                                     │
                                                                     ▼
                                                              ┌──────────────┐
                                                              │ 5. Predict   │
                                                              │    (Infer)   │
                                                              │              │
                                                              │ Upload new   │
                                                              │ photo → get  │
                                                              │ results      │
                                                              └──────────────┘
```

---

## Step-by-Step Walkthrough

### Step 1: Collect and Organize Photos

**Where photos go:** `datasets/raw_images/`

Photos must be organized into folders named by progress percentage:

```
datasets/raw_images/
├── 10%/          ← photos of sites that are 10% complete
│   ├── photo001.jpg
│   ├── photo002.jpg
│   └── ...
├── 15%/          ← photos of sites that are 15% complete
│   ├── photo003.jpg
│   └── ...
├── 20%/
├── 25%/
├── 30%/
├── 40%
└── 50%/
```

**Why folder names matter:** The classification model learns from these folder names. Each folder is a "class" (category). The model learns the visual difference between 10% and 50% progress.

### Step 2: Annotate (Label) the Photos

**Where labels go:** `datasets/labels/`

Use the web annotation tool (at `/annotate/:datasetName/:index`) to draw bounding boxes around construction elements in each photo.

Each label file is a `.txt` file with the same name as the image (e.g., `photo001.txt`). The format is:

```
# progress: 30%
0 0.45 0.52 0.30 0.25
1 0.60 0.35 0.15 0.20
```

Each line represents one bounding box:

| Value | Meaning |
|---|---|
| First number | Object class (0=foundation, 1=column, 2=beam, 3=roof, 4=wall, 5=floor) |
| 2nd number | X center of box (0.0 to 1.0, fraction of image width) |
| 3rd number | Y center of box (0.0 to 1.0, fraction of image height) |
| 4th number | Width of box (0.0 to 1.0) |
| 5th number | Height of box (0.0 to 1.0) |

This is called **YOLO format** — it's a standard way to describe where objects are in an image.

### Step 3: Split the Dataset

**Command:**
```bash
cd server
python split_dataset.py
```

**What it does:** Divides your photos into two groups:
- **Training set (80%)** — photos the AI learns from
- **Validation set (20%)** — photos used to test how well the AI learned

**Why split?** If the AI only saw the same photos it trained on, it could just memorize them. The validation set checks if the AI truly learned general patterns, not just memorized specific photos.

**Configuration** is in `configs/dataset.yaml`:

```yaml
dataset_type: "detection"     # Change to "classification" for classification split
train_ratio: 0.8              # 80% for training
val_ratio: 0.2                # 20% for validation
test_ratio: 0                 # 0% for testing (can add later)
seed: 42                      # Random seed for reproducibility
```

**Output:** Creates two folders:
- `datasets/split_classification/` — organized by class folder (10%, 15%, etc.)
- `datasets/split_detection/` — organized as images/ and labels/ subfolders

### Step 4: Train the Models

There are **three** training options. The two YOLO-based ones are the main ones used:

#### Option A: Classification Model (Predicts Progress %)

```bash
cd server/ml_scripts/classification
python train_classification.py
```

**What happens under the hood:**
1. Loads a pretrained YOLO model (`yolo11n-cls.pt`) that already knows how to recognize general visual patterns
2. Fine-tunes it on your construction photos so it learns what 10%, 20%, 50% progress looks like
3. Applies **data augmentation** — creates variations of each photo by flipping, changing colors, and applying random distortions. This helps the model generalize better.
4. Runs for 100 epochs (passes through the entire dataset)
5. Saves the best model to `models/progress-classification.pt`

#### Option B: Detection Model (Finds Construction Elements)

```bash
cd server/ml_scripts/detection
python train_detection.py
```

**What happens under the hood:**
1. Loads a pretrained YOLO detection model (`yolo11n.pt`)
2. Fine-tunes it to recognize 6 construction elements: foundation, column, beam, roof, wall, floor
3. Uses your annotated bounding boxes to learn where each element appears
4. Runs for 100 epochs
5. Saves the best model to `models/progress-detection.pt`

#### Option C: Custom Regression Model (in `train.py`)

```bash
cd server
python train.py
```

This is a simpler custom-built neural network (not YOLO-based) that directly predicts a progress number between 0 and 1. It uses:
- A small convolutional neural network (CNN) with 4 layers
- MSE loss (mean squared error) to measure prediction accuracy
- Early stopping — stops training if the model stops improving
- Learning rate scheduling — gradually reduces learning speed

**Configuration** is in `configs/training.yaml` (referenced by train.py).

### Step 5: Predict (Run Inference)

When a user uploads a photo through the web interface:

1. The backend receives the image via `POST /api/predict`
2. The image is saved to a temporary file
3. **Both models run on the image:**
   - Classification model returns top 5 progress predictions with confidence scores
   - Detection model returns bounding boxes for found construction elements
4. Results are combined and returned as JSON:

```json
{
  "classification": [
    {"class": "30%", "confidence": 0.92},
    {"class": "25%", "confidence": 0.05},
    ...
  ],
  "detection": [
    {
      "class": "column",
      "confidence": 0.88,
      "bbox": {"x1": 120, "y1": 80, "x2": 200, "y2": 300},
      "center": {"x": 160, "y": 190},
      "dimensions": {"width": 80, "height": 220}
    },
    ...
  ],
  "overall_progress": "30%",
  "progress_confidence": 0.92
}
```

---

## How the Code Works

### Data Augmentation

Data augmentation is the process of creating modified versions of your training photos to make the model more robust. Here's what each technique does:

| Technique | What It Does | Why It Helps |
|---|---|---|
| **Resize to 640x640** | Makes all images the same size | Models need consistent input size |
| **Random Horizontal Flip** | Mirrors the image left-to-right (50% chance) | Photos could be taken from either side |
| **Random Vertical Flip** | Flips the image upside down | (Mainly for classification) Adds variety |
| **Color Jitter** | Randomly changes brightness, contrast, saturation, hue | Handles different lighting conditions on site |
| **RandAugment** | Applies a random combination of transformations | General robustness to variations |
| **Random Erasing** | Randomly blacks out a patch of the image | Simulates occlusion (objects blocking the view) |
| **Normalization** | Scales pixel values to a standard range | Helps the model converge faster during training |

### Training Techniques

| Technique | What It Does | Why It Helps |
|---|---|---|
| **Transfer Learning** | Starts from a model pretrained on millions of images | The model already knows basic visual patterns (edges, textures, shapes) — your data only needs to teach it construction-specific patterns |
| **Early Stopping** | Stops training when validation loss stops improving | Prevents overfitting (memorizing training data instead of learning patterns) |
| **Cosine Annealing LR** | Gradually reduces the learning rate in a smooth curve | Helps the model settle into better solutions |
| **Gradient Clipping** | Limits how much the model can change in one step | Prevents unstable training jumps |
| **Dropout (0.3–0.5)** | Randomly disables neurons during training | Forces the model to learn redundant patterns, making it more robust |

### Model Architecture

**Classification (YOLO-based):**
- Base: YOLO11n-cls (nano version — small and fast)
- Input: 640x640 RGB image
- Output: Probability for each progress class (10%, 15%, 20%, 25%, 30%, 40%, 50%)

**Detection (YOLO-based):**
- Base: YOLO11n (nano version)
- Input: 640x640 RGB image
- Output: Bounding boxes + class labels for 6 construction elements

**Custom Regression (in train.py):**
- A simple CNN: 3 convolutional layers → pooling → 3 fully connected layers
- Input: 640x640 RGB image
- Output: Single number 0–1 representing progress percentage

---

## How to Make the Model More Accurate

### 1. Add More Training Data (Most Impactful)

The single biggest factor in model accuracy is the amount and quality of training data.

**What to do:**
- **More photos per class:** Aim for at least 50–100 photos per progress percentage (10%, 15%, etc.)
- **More progress levels:** If you only have 7 classes (10%, 15%, 20%, 25%, 30%, 40%, 50%), consider adding 5%, 35%, 45%, etc.
- **Diverse conditions:** Include photos from different angles, lighting, weather, and construction sites
- **Similar photo counts per class:** Try to have roughly equal numbers of photos in each folder. If "10%" has 200 photos but "50%" has only 10, the model will be biased toward 10%.

**How to check your data balance:**
```bash
# Count images per progress level
for dir in datasets/raw_images/*/; do echo "$dir: $(ls "$dir" | wc -l) images"; done
```

### 2. Improve Annotation Quality (For Detection Model)

Better bounding box annotations directly lead to better detection.

**What to do:**
- Draw **tight** boxes around objects — don't include lots of empty space
- Be **consistent** — always include the entire object, not just parts
- **Annotate all objects** in each image, not just some
- Don't annotate very small or unclear objects — these confuse the model
- Review existing annotations for errors

**How to check annotation rate:**
The split script prints how many images have labels. If you see "Labels missing: 50/100 (50.0%)" — half your images have no annotations.

### 3. Use Data Augmentation Strategically

The current augmentation is already reasonable, but you can tune it:

**In `train_classification.py` and `train.py`, adjust:**

| Parameter | Current | When to Increase | When to Decrease |
|---|---|---|---|
| `brightness` | 0.2 | Photos have varying lighting | Photos already consistent |
| `contrast` | 0.2 | Hazy or overexposed photos | High-quality, well-lit photos |
| `saturation` | 0.2 | Varied camera types | Consistent camera |
| `hue` | 0.1 | Very diverse color conditions | Color matters for classification |
| `flip probability` | 0.5 | Limited data | Very asymmetric scenes |
| `Random Erasing` | enabled | Small dataset, risk of overfitting | Large dataset |

### 4. Tune Training Parameters

**In `train_classification.py`:**
```python
# Try these changes:
results = model.train(
    data="../../datasets/split_classification",
    epochs=200,        # Increase from 100 if model is still improving
    imgsz=640,         # Try 1024 or 1280 for higher-resolution images
    batch=16,          # Smaller batch if running out of GPU memory
    lr0=0.001,         # Lower learning rate for fine-grained learning
    patience=30,       # More patience before early stopping
)
```

**In `train_detection.py`:**
```python
results = model.train(
    data="../../datasets/detection.yaml",
    epochs=200,
    imgsz=640,         # Higher resolution = better small object detection
    batch=16,
)
```

**Key parameters explained:**

| Parameter | What It Controls | Recommended Range |
|---|---|---|
| `epochs` | How many times the model sees all training data | 100–300 |
| `imgsz` | Image resolution during training | 640 (fast), 1024 (balanced), 1280 (best quality) |
| `batch` | How many images processed at once | 8–32 (limited by GPU memory) |
| `lr0` | How fast the model learns | 0.0001–0.01 |
| `patience` | Epochs to wait before early stopping | 20–50 |

### 5. Use a Larger Base Model

Currently both models use the "nano" (smallest) YOLO variant. Larger models are more accurate but slower:

| Model | Speed | Accuracy | When to Use |
|---|---|---|---|
| `yolo11n-cls.pt` / `yolo11n.pt` | Fastest | Good | Limited GPU, real-time needs |
| `yolo11s-cls.pt` / `yolo11s.pt` | Fast | Better | Good balance |
| `yolo11m-cls.pt` / `yolo11m.pt` | Medium | Great | Server deployment, best accuracy |
| `yolo11l-cls.pt` / `yolo11l.pt` | Slow | Excellent | Maximum accuracy needed |

**To switch, change the model load line:**
```python
# In train_classification.py:
model = YOLO("../../models/yolo11s-cls.pt")   # s = small, or m = medium

# In train_detection.py:
model = YOLO("../../models/yolo11s.pt")        # s = small, or m = medium
```

### 6. Add More Granular Progress Classes

Currently the model predicts one of 7 categories (10%, 15%, 20%, 25%, 30%, 40%, 50%). The gaps between classes are uneven:
- 10→15 (5% gap)
- 15→20 (5% gap)
- 20→25 (5% gap)
- 25→30 (5% gap)
- 30→40 (10% gap) ← big jump
- 40→50 (10% gap) ← big jump

**What to do:**
- Add intermediate classes: 35%, 45%
- Consider using 5% increments throughout: 10%, 15%, 20%, 25%, 30%, 35%, 40%, 45%, 50%
- Ensure each class has enough photos (50+)

### 7. Validate and Evaluate

**Run validation after training:**
```bash
cd server/ml_scripts/classification
python val_classification.py
```

This reports:
- **Top-1 accuracy:** How often the model's #1 prediction is correct
- **Top-5 accuracy:** How often the correct answer is in the model's top 5 predictions

**What good numbers look like:**
- Top-1 accuracy > 70%: Decent
- Top-1 accuracy > 85%: Good
- Top-1 accuracy > 95%: Excellent

**If accuracy is low:**
- Check if you have enough data per class
- Verify photos are in the correct folders
- Look at misclassified images to understand what confuses the model
- Consider if some classes are too similar visually (e.g., 20% vs 25% might look very similar)

### 8. Common Mistakes to Avoid

| Mistake | Why It Hurts | Fix |
|---|---|---|
| Very few photos per class | Model can't learn meaningful patterns | Collect at least 50+ photos per class |
| Unequal class sizes | Model becomes biased toward larger classes | Balance by collecting more data or undersampling |
| Mixed image quality | Model learns noise instead of patterns | Filter out blurry, dark, or irrelevant photos |
| Wrong folder placement | Model learns wrong labels | Double-check photos are in the correct progress folder |
| Skipping validation split | You can't tell if the model is actually good | Always set aside 15-20% for validation |
| Over-training | Model memorizes training data (overfitting) | Use early stopping (already enabled) |

### 9. Quick Accuracy Improvement Checklist

When you want better results, go through this list in order (most impactful first):

- [ ] Add more photos to classes with fewer images
- [ ] Ensure all photos in a folder actually match that progress level
- [ ] Annotate more images (for detection model)
- [ ] Try a larger model (nano → small → medium)
- [ ] Increase training epochs (100 → 200)
- [ ] Increase image resolution (640 → 1024)
- [ ] Add missing progress levels (e.g., 35%, 45%)
- [ ] Fine-tune learning rate (try 0.0005)
- [ ] Review and fix bad annotations

---

## Quick Reference: File Map

```
server/
├── api.py                              # Main API server — handles prediction requests
├── train.py                            # Custom regression model training
├── split_dataset.py                    # Splits data into train/val sets
├── custom_dataset.py                   # Loads images + labels for train.py
├── configs/
│   ├── dataset.yaml                    # Data split configuration
│   └── training.yaml                   # Training hyperparameters
├── datasets/
│   ├── raw_images/                     # Your photos organized by progress %
│   │   ├── 10%/
│   │   ├── 15%/
│   │   └── ...
│   ├── labels/                         # YOLO-format annotation files
│   ├── split_classification/           # Auto-generated: classification training data
│   │   ├── train/
│   │   └── val/
│   └── split_detection/                # Auto-generated: detection training data
│       ├── train/images/ + labels/
│       └── val/images/ + labels/
├── ml_scripts/
│   ├── classification/
│   │   ├── train_classification.py     # Train progress % prediction model
│   │   ├── val_classification.py       # Validate classification accuracy
│   │   └── models/                     # Saved classification model
│   │       └── progress-classification.pt
│   └── detection/
│       ├── train_detection.py          # Train object detection model
│       ├── val_detection.py            # Validate detection accuracy
│       └── models/                     # Saved detection model
│           └── progress-detection.pt
├── api_handlers/
│   └── ml_handler.py                   # Runs both models on uploaded images
└── dto/                                # Data models for API communication
```

---

## Troubleshooting

### "No images found" when splitting dataset
- Check that `datasets/raw_images/` has subfolders named with percentages (e.g., `10%`, `15%`)
- Check that images are `.jpg`, `.jpeg`, `.png`, `.bmp`, or `.tiff` format

### Training loss doesn't decrease
- Verify you have enough data (at least 20+ images per class)
- Try a lower learning rate (0.0001)
- Check that images aren't all identical

### Model always predicts the same class
- Your data is likely imbalanced (one class has many more photos)
- Collect more data for underrepresented classes

### CUDA out of memory during training
- Reduce batch size (try 8 or 4)
- Reduce image size (try 320 instead of 640)
- Use a smaller model variant

### Detection model finds nothing
- Ensure you have enough annotated images with bounding boxes
- Check that label files exist in `datasets/labels/`
- Verify label files have correct YOLO format (5 numbers per line)

### Classification accuracy is low
- Check if photos are in the wrong folders
- Ensure similar-looking classes (e.g., 20% vs 25%) have distinct visual differences
- Add more training data
- Try a larger model
