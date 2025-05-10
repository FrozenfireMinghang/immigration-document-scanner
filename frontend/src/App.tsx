import React, { useState, useEffect } from 'react';
import DocumentUploader from './components/DocumentUploader';
import FieldEditor from './components/FieldEditor';
import { ExtractionResponse, ExtractedField } from './types';
import './App.css';

const App: React.FC = () => {
  const [extractedFields, setExtractedFields] = useState<ExtractedField[]>([]);
  const [documentType, setDocumentType] = useState<string>('');
  const [originalUrl, setOriginalUrl] = useState<string>('');
  const [processedUrl, setProcessedUrl] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentId, setCurrentId] = useState<number | null>(null);
  const [recentDocs, setRecentDocs] = useState<any[]>([]);

  const allowedFields = [
    "full_name", "date_of_birth", "number", "category",
    "card_expires_date", "country", "issue_date", "expiration_date"
  ];

  const loadRecentDocs = async () => {
    const res = await fetch("http://localhost:8000/recent");
    const data = await res.json();
    setRecentDocs(data);
  };

  useEffect(() => {
    loadRecentDocs();
  }, []);

  const handleSave = async () => {
    const defaultPayload: Record<string, string | null> = Object.fromEntries(
      allowedFields.map(field => [field, null])
    );

    const actualFields = Object.fromEntries(
      extractedFields
        .filter(f => allowedFields.includes(f.field_name))
        .map(f => [f.field_name, f.value])
    );

    const payload = {
      id: currentId,
      document_type: documentType,
      file_name: fileName,
      original_image_url: originalUrl,
      processed_image_url: processedUrl,
      ...defaultPayload,
      ...actualFields
    };

    const res = await fetch("http://localhost:8000/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    setSuccessMsg("✅ Saved to database!");
    setTimeout(() => setSuccessMsg(""), 3000);
    setCurrentId(result.id);
    loadRecentDocs();
  };

  const handleRecentClick = (doc: any) => {
    const fields = Object.entries(doc)
      .filter(([k, _]) => allowedFields.includes(k))
      .map(([field_name, value]) => ({ field_name, value: value ?? '' }));

    setExtractedFields(fields);
    setDocumentType(doc.document_type);
    setOriginalUrl(doc.original_image_url);
    setProcessedUrl(doc.processed_image_url);
    setFileName(doc.file_name);
    setCurrentId(doc.id);
    setSuccessMsg("✅ Loaded entry successfully");
    setTimeout(() => setSuccessMsg(""), 3000);
  };

  return (
    <div className="app-wrapper">
      <header className="app-header">Immigration Document Scanner 🔍</header>
      {successMsg && <div className="success-banner">{successMsg}</div>}
      {errorMsg && <div className="error-banner">{errorMsg}</div>}
      <div className="app-container">
        <div className="sidebar">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <input
              type="file"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  const file = e.target.files[0];
                  setFileName(e.target.value);
                  setSelectedFile(file);
                  setCurrentId(null);
                }
              }}
              className="native-file-input"
            />
            <DocumentUploader
              file={selectedFile}
              onExtracted={(data: ExtractionResponse) => {
                const fields = Object.entries(data.document_content).map(([field_name, value]) => ({
                  field_name,
                  value,
                }));
                setExtractedFields(fields);
                setDocumentType(data.document_type);
                setOriginalUrl(data.original_image_url || '');
                setProcessedUrl(data.processed_image_url || '');
                setSuccessMsg('✅ Fields extracted successfully.');
                setErrorMsg('');
                setTimeout(() => setSuccessMsg(''), 3000);
              }}
              onError={(msg: string) => {
                setErrorMsg(`❌ ${msg}`);
                setTimeout(() => setErrorMsg(''), 4000);
              }}
            />
          </div>

          <div className="file-name-label">{fileName}</div>
          <div className="section-title" style={{ marginTop: '36px' }}>📚 Recent Extractions</div>
          <div style={{ fontWeight: 'bold', color: '#ccc', marginTop: '20px', fontSize: '0.95rem' }}>
            ID - Name - Document Type
          </div>
          <div className="history">
            {recentDocs.slice(0, 10).map((doc) => (
              <div key={doc.id} className="history-entry" onClick={() => handleRecentClick(doc)}>
                {`${doc.id} - ${doc.full_name || 'Unnamed'} - ${doc.document_type}`}
              </div>
            ))}
          </div>
        </div>

        <div className="main">
          <div className="section-title">📄 Original Document View</div>
          {originalUrl && <img src={originalUrl} className="preview" alt="original" />}
          <div className="section-title">✂️ After Removing White Borders</div>
          {processedUrl && <img src={processedUrl} className="preview" alt="processed" />}
        </div>

        <div className="editor">
          <div className="section-title" style={{ marginBottom: '24px' }}>📖 Display Extracted Fields</div>
          {documentType && <h3>Type: {documentType}</h3>}
          {extractedFields.length > 0 && (
            <FieldEditor fields={extractedFields} onUpdate={setExtractedFields} />
          )}
          <button className="save-btn" onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  );
};

export default App;