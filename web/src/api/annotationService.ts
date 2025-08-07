import axios from "axios";

export const VITE_BASE_API = import.meta.env.VITE_BASE_API;

export interface Annotation {
  imageName: string;
  progress: number; // 0-100
  boxes: Array<{
    classId: number;
    xCenter: number;
    yCenter: number;
    width: number;
    height: number;
  }>;
}

export interface Dataset {
  name: string;
  image_count: number;
  annotated_count: number;
  progress: number;
}

export interface PercentageDataset {
  annotated: boolean;
  path: string;
  progress: number;
  boxes: Array<{
    classId: number;
    xCenter: number;
    yCenter: number;
    width: number;
    height: number;
  }>;
}

export async function fetchDatasets(): Promise<Dataset[]> {
  const response = await axios.get(`${VITE_BASE_API}/datasets`);

  return response.data;
}

export async function fetchPercentageDataset(
  datasetName: string
): Promise<PercentageDataset[]> {
  const encodedName = encodeURIComponent(datasetName);
  const response = await axios.get(`${VITE_BASE_API}/datasets/${encodedName}`);
  return response.data;
}

export async function fetchImages(datasetName?: string): Promise<string[]> {
  const url = datasetName
    ? `${VITE_BASE_API}/datasets/${encodeURIComponent(datasetName)}/images`
    : `${VITE_BASE_API}/images`;
  const response = await axios.get(url);
  return response.data;
}

export async function saveAnnotation(
  annotation: Annotation,
  datasetName?: string
): Promise<void> {
  const url = datasetName
    ? `${VITE_BASE_API}/datasets/${encodeURIComponent(datasetName)}/annotations`
    : `${VITE_BASE_API}/annotations`;
  await axios.post(url, annotation);
}
