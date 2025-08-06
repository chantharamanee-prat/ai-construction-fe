import axios from "axios";

const BASE_API = import.meta.env.VITE_BASE_API

export interface Dataset {
  name: string
  image_count: number
  annotated_count: number
  progress: number
}

export async function fetchDatasets(): Promise<Dataset[]> {
    const response = await axios.get(`${BASE_API}/datasets`)

    return response.data
}