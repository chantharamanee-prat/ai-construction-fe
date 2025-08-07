import React, { useState, useRef } from "react";
import { predictImage } from "../api/predictionService";

interface Prediction {
  class: string;
  confidence: number;
}

export default function MLPredictPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      setPredictions([]);

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
      setPredictions(result.predictions);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setPredictions([]);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
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
          <img
            src={previewUrl}
            alt="Preview"
            style={{
              maxWidth: "100%",
              maxHeight: "400px",
              border: "1px solid #ddd",
              borderRadius: "4px",
            }}
          />
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
      {predictions.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h3>Prediction Results:</h3>
          <div
            style={{
              // backgroundColor: "#d4edda",
              border: "1px solid #c3e6cb",
              borderRadius: "4px",
              padding: "20px",
            }}
          >
            {predictions.map((prediction, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "10px 0",
                  borderBottom:
                    index < predictions.length - 1
                      ? "1px solid #c3e6cb"
                      : "none",
                }}
              >
                <span style={{ fontWeight: "bold" }}>{prediction.class}</span>
                <span>{(prediction.confidence * 100).toFixed(2)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
