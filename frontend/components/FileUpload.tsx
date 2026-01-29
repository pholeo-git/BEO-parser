'use client';

import React, { useCallback, useState } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
  error?: string;
}

export default function FileUpload({
  onFileSelect,
  selectedFile,
  error,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file && file.type === 'application/pdf') {
        onFileSelect(file);
      } else {
        onFileSelect(null);
      }
    },
    [onFileSelect]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file && file.type === 'application/pdf') {
        onFileSelect(file);
      } else {
        onFileSelect(null);
      }
    },
    [onFileSelect]
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${isDragging ? '#045559' : '#cef0f1'}`,
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          backgroundColor: isDragging ? '#eaf3f4' : '#fffaf0',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        {selectedFile ? (
          <div>
            <p style={{ color: '#045559', marginBottom: '8px', fontWeight: 'bold' }}>
              {selectedFile.name}
            </p>
            <p style={{ color: '#3f4040', fontSize: '14px' }}>
              {formatFileSize(selectedFile.size)}
            </p>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onFileSelect(null);
              }}
              style={{
                marginTop: '12px',
                padding: '6px 12px',
                backgroundColor: '#3f4040',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
              }}
            >
              Remove
            </button>
          </div>
        ) : (
          <div>
            <p style={{ color: '#045559', marginBottom: '8px' }}>
              Drag and drop your PDF here, or click to browse
            </p>
            <p style={{ color: '#3f4040', fontSize: '14px' }}>
              PDF files only (no size limit)
            </p>
          </div>
        )}
      </div>
      {error && (
        <p style={{ color: '#d32f2f', fontSize: '14px', marginTop: '8px' }}>
          {error}
        </p>
      )}
    </div>
  );
}
