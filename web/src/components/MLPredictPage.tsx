import React, { useState, useRef } from "react";
import { predictImage } from "../api/predictionService";
import type {
  PredictionResult,
  ClassificationPrediction,
  DetectionPrediction,
} from "../api/predictionService";
import {
  CLASS_NAMES,
  CLASS_COLORS,
  type ClassId,
} from "./AnnotationTool/ClassSelector";

interface Prediction {
  class: string;
  confidence: number;
}

export default function MLPredictPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] =
    useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageSize, setImageSize] = useState<{
    width: number;
    height: number;
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        setError("Please select a valid image file");
        return;
      }

      setSelectedFile(file);
      setError(null);
      setPredictionResult(null);

      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handlePredict = async () => {
    if (!selectedFile) {
      setError("Please select an image first");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await predictImage(selectedFile);
      setPredictionResult(result.predictions);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setPredictionResult(null);
    setError(null);
    setImageSize(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleImageLoad = () => {
    if (imageRef.current) {
      setImageSize({
        width: imageRef.current.naturalWidth,
        height: imageRef.current.naturalHeight,
      });
    }
  };

  // Helper function to get class color based on class name
  const getClassColor = (className: string): string => {
    // Find the class ID based on class name
    for (const [id, name] of Object.entries(CLASS_NAMES)) {
      if (name === className) {
        return CLASS_COLORS[parseInt(id) as ClassId];
      }
    }
    // Fallback color if class not found
    return "#ff4444";
  };

  // Helper function to render detection boxes
  const renderDetectionBoxes = () => {
    if (!predictionResult?.detection || !imageRef.current || !imageSize) {
      return null;
    }

    const img = imageRef.current;
    const displayWidth = img.offsetWidth;
    const displayHeight = img.offsetHeight;

    const scaleX = displayWidth / imageSize.width;
    const scaleY = displayHeight / imageSize.height;

    return predictionResult.detection.map((detection, index) => {
      const { bbox } = detection;
      const left = bbox.x1 * scaleX;
      const top = bbox.y1 * scaleY;
      const width = (bbox.x2 - bbox.x1) * scaleX;
      const height = (bbox.y2 - bbox.y1) * scaleY;

      // Get the appropriate color for this class
      const classColor = getClassColor(detection.class);

      return (
        <div
          key={index}
          style={{
            position: "absolute",
            left: `${left}px`,
            top: `${top}px`,
            width: `${width}px`,
            height: `${height}px`,
            border: `2px solid ${classColor}`,
            backgroundColor: `${classColor}20`, // 20 is hex for low opacity
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: "-25px",
              left: "0",
              backgroundColor: classColor,
              color: "white",
              padding: "2px 6px",
              fontSize: "12px",
              borderRadius: "3px",
              whiteSpace: "nowrap",
              textShadow: "1px 1px 1px rgba(0,0,0,0.5)",
            }}
          >
            {detection.class} ({(detection.confidence * 100).toFixed(1)}%)
          </div>
        </div>
      );
    });
  };

  return (
    <div
      style={{
        padding: "20px",
        maxWidth: "800px",
        margin: "0 auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1 style={{ textAlign: "center", marginBottom: "30px" }}>
        ML Prediction
      </h1>

      {/* File Upload Section */}
      <div
        style={{
          border: "2px dashed #ccc",
          padding: "40px",
          textAlign: "center",
          borderRadius: "8px",
          marginBottom: "20px",
          backgroundColor: "#f9f9f9",
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="image/*"
          style={{ display: "none" }}
        />

        {!selectedFile ? (
          <div>
            <p
              style={{ marginBottom: "20px", fontSize: "18px", color: "#666" }}
            >
              Upload an image to get ML predictions
            </p>
            <button
              onClick={handleUploadClick}
              style={{
                padding: "12px 24px",
                fontSize: "16px",
                backgroundColor: "#6c757d",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Choose Image
            </button>
          </div>
        ) : (
          <div>
            <p
              style={{ marginBottom: "15px", fontSize: "16px", color: "#666" }}
            >
              Selected: {selectedFile.name}
            </p>
            <div style={{ marginBottom: "15px" }}>
              <button
                onClick={handleUploadClick}
                style={{
                  padding: "8px 16px",
                  fontSize: "14px",
                  backgroundColor: "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  marginRight: "10px",
                }}
              >
                Choose Different Image
              </button>
              <button
                onClick={handleReset}
                style={{
                  padding: "8px 16px",
                  fontSize: "14px",
                  backgroundColor: "#dc3545",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Reset
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Image Preview */}
      {previewUrl && (
        <div style={{ textAlign: "center", marginBottom: "20px" }}>
          <h3>Image Preview:</h3>
          <div style={{ position: "relative", display: "inline-block" }}>
            <img
              ref={imageRef}
              src={previewUrl}
              alt="Preview"
              onLoad={handleImageLoad}
              style={{
                maxWidth: "100%",
                maxHeight: "400px",
                border: "1px solid #ddd",
                borderRadius: "4px",
              }}
            />
            {renderDetectionBoxes()}
          </div>
        </div>
      )}

      {/* Predict Button */}
      {selectedFile && (
        <div style={{ textAlign: "center", marginBottom: "20px" }}>
          <button
            onClick={handlePredict}
            disabled={isLoading}
            style={{
              padding: "12px 30px",
              fontSize: "18px",
              backgroundColor: isLoading ? "#ccc" : "#28a745",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: isLoading ? "not-allowed" : "pointer",
            }}
          >
            {isLoading ? "Predicting..." : "Run Prediction"}
          </button>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div
          style={{
            backgroundColor: "#f8d7da",
            color: "#721c24",
            padding: "12px",
            borderRadius: "4px",
            marginBottom: "20px",
            border: "1px solid #f5c6cb",
          }}
        >
          Error: {error}
        </div>
      )}

      {/* Results Section */}
      {predictionResult && (
        <div style={{ marginTop: "30px" }}>
          {/* Classification Results */}
          {predictionResult.classification &&
            predictionResult.classification.length > 0 && (
              <div style={{ marginBottom: "30px" }}>
                <h3>Classification Results:</h3>
                <div
                  style={{
                    border: "1px solid #c3e6cb",
                    borderRadius: "4px",
                    padding: "20px",
                  }}
                >
                  {predictionResult.classification.map((prediction, index) => (
                    <div
                      key={index}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        padding: "10px 0",
                        borderBottom:
                          index < predictionResult.classification.length - 1
                            ? "1px solid #c3e6cb"
                            : "none",
                      }}
                    >
                      <span style={{ fontWeight: "bold" }}>
                        {prediction.class}
                      </span>
                      <span>{(prediction.confidence * 100).toFixed(2)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* No Results Message */}
          {(!predictionResult.classification ||
            predictionResult.classification.length === 0) &&
            (!predictionResult.detection ||
              predictionResult.detection.length === 0) && (
              <div style={{ marginTop: "30px" }}>
                <h3>No Results Found</h3>
                <div
                  style={{
                    backgroundColor: "#f8d7da",
                    border: "1px solid #f5c6cb",
                    borderRadius: "4px",
                    padding: "20px",
                    color: "#721c24",
                  }}
                >
                  No objects or classifications were detected in this image.
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
