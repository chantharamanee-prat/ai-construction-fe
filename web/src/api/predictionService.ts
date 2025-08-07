import axios from "axios";
import { VITE_BASE_API } from "./annotationService";

export interface Prediction {
  class: string;
  confidence: number;
}

export interface PredictionResponse {
  predictions: Prediction[];
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
