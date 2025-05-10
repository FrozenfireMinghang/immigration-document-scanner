export interface ExtractedField {
  field_name: string;
  value: string;
}

export interface ExtractionResponse {
  document_type: string;
  document_content: Record<string, string>;
  original_image_url: string;
  processed_image_url: string;
}