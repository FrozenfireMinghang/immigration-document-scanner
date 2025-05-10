import axios from 'axios';
import { ExtractionResponse } from './types';

const BASE_URL = 'http://localhost:8000';

export const uploadAndExtract = async (file: File): Promise<ExtractionResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${BASE_URL}/classify_and_extract`, formData);
  return response.data;
};
