import React, { useState } from 'react';
import { uploadAndExtract } from '../api';
import { ExtractionResponse } from '../types';

interface Props {
  file: File | null;
  onExtracted: (data: ExtractionResponse) => void;
  onError?: (errorMsg: string) => void;
}

const DocumentUploader: React.FC<Props> = ({ file, onExtracted, onError }) => {
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const result = await uploadAndExtract(file);
      onExtracted(result);
    } catch (e: any) {
      if (e?.response?.status === 400) {
        const error = await e.response.json();
        onError?.(error.error || 'Extraction failed. Please try another document.');
      } else {
        onError?.('Extraction failed. Please try another document.');
      }
    }
    setLoading(false);
  };

  return (
    <button onClick={handleUpload} disabled={!file || loading}>
      {loading ? 'Extracting...' : 'Extract Fields'}
    </button>
  );
};

export default DocumentUploader;