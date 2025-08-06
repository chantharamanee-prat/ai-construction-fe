import axios from 'axios';

const API_BASE_URL = '/api';

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

export async function fetchImages(): Promise<string[]> {
  const response = await axios.get(`${API_BASE_URL}/images`);
  return response.data;
}

export async function saveAnnotation(annotation: Annotation): Promise<void> {
  await axios.post(`${API_BASE_URL}/annotations`, annotation);
}
