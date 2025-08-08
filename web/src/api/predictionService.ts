import axios from "axios";
import { VITE_BASE_API } from "./annotationService";

export interface ClassificationPrediction {
  class: string;
  confidence: number;
}

export interface DetectionPrediction {
  class: string;
  confidence: number;
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  center: {
    x: number;
    y: number;
  };
  dimensions: {
    width: number;
    height: number;
  };
}

export interface PredictionResult {
  classification: ClassificationPrediction[];
  detection: DetectionPrediction[];
  overall_progress: string | null;
  progress_confidence: number;
}

export interface PredictionResponse {
  predictions: PredictionResult;
}

// Legacy interface for backward compatibility
export interface Prediction {
  class: string;
  confidence: number;
}

export async function predictImage(file: File): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${VITE_BASE_API}/predict`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Prediction request failed"
      );
    }
    throw new Error("Prediction request failed");
  }
}
