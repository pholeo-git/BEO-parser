'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import FileUpload from './FileUpload';
import { uploadSubmission, checkStatus, SubmissionStatus } from '../lib/api';

interface FormData {
  name: string;
  email: string;
  event_name?: string;
}

export default function BEOForm() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submissionId, setSubmissionId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    if (!selectedFile) {
      setSubmitError('Please select a PDF file');
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    try {
      const response = await uploadSubmission({
        name: data.name,
        email: data.email,
        event_name: data.event_name,
        pdf_file: selectedFile,
      });

      setSubmissionId(response.submission_id);
      setSubmitSuccess(
        `File uploaded successfully! Processing will begin shortly. You'll receive an email at ${data.email} when your files are ready.`
      );

      // Reset form
      reset();
      setSelectedFile(null);

      // Optionally poll for status updates
      // pollStatus(response.submission_id);
    } catch (error: any) {
      setSubmitError(
        error.response?.data?.detail || error.message || 'An error occurred. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: '600px',
        margin: '0 auto',
        padding: '40px 20px',
      }}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '40px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <h1
          style={{
            fontFamily: 'var(--font-koho)',
            fontSize: '32px',
            color: '#045559',
            marginBottom: '8px',
            fontWeight: 500,
          }}
        >
          BEO Separator
        </h1>
        <p
          style={{
            color: '#3f4040',
            marginBottom: '32px',
            fontSize: '16px',
          }}
        >
          Upload your BEO packet PDF to split it into individual BEO files.
        </p>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div style={{ marginBottom: '24px' }}>
            <label
              htmlFor="name"
              style={{
                display: 'block',
                marginBottom: '8px',
                color: '#3f4040',
                fontWeight: 'bold',
                fontSize: '14px',
              }}
            >
              Name <span style={{ color: '#d32f2f' }}>*</span>
            </label>
            <input
              id="name"
              type="text"
              {...register('name', { required: 'Name is required' })}
              style={{
                width: '100%',
                padding: '12px',
                border: `1px solid ${errors.name ? '#d32f2f' : '#cef0f1'}`,
                borderRadius: '10px',
                fontSize: '16px',
                fontFamily: 'var(--font-open-sans)',
              }}
            />
            {errors.name && (
              <p style={{ color: '#d32f2f', fontSize: '14px', marginTop: '4px' }}>
                {errors.name.message}
              </p>
            )}
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label
              htmlFor="email"
              style={{
                display: 'block',
                marginBottom: '8px',
                color: '#3f4040',
                fontWeight: 'bold',
                fontSize: '14px',
              }}
            >
              Email <span style={{ color: '#d32f2f' }}>*</span>
            </label>
            <input
              id="email"
              type="email"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
              })}
              style={{
                width: '100%',
                padding: '12px',
                border: `1px solid ${errors.email ? '#d32f2f' : '#cef0f1'}`,
                borderRadius: '10px',
                fontSize: '16px',
                fontFamily: 'var(--font-open-sans)',
              }}
            />
            {errors.email && (
              <p style={{ color: '#d32f2f', fontSize: '14px', marginTop: '4px' }}>
                {errors.email.message}
              </p>
            )}
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label
              htmlFor="event_name"
              style={{
                display: 'block',
                marginBottom: '8px',
                color: '#3f4040',
                fontWeight: 'bold',
                fontSize: '14px',
              }}
            >
              Event Name (optional)
            </label>
            <input
              id="event_name"
              type="text"
              {...register('event_name')}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #cef0f1',
                borderRadius: '10px',
                fontSize: '16px',
                fontFamily: 'var(--font-open-sans)',
              }}
            />
          </div>

          <div style={{ marginBottom: '32px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                color: '#3f4040',
                fontWeight: 'bold',
                fontSize: '14px',
              }}
            >
              PDF File <span style={{ color: '#d32f2f' }}>*</span>
            </label>
            <FileUpload
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
              error={!selectedFile && submitError ? 'Please select a PDF file' : undefined}
            />
          </div>

          {submitError && (
            <div
              style={{
                padding: '12px',
                backgroundColor: '#ffebee',
                color: '#d32f2f',
                borderRadius: '10px',
                marginBottom: '24px',
                fontSize: '14px',
              }}
            >
              {submitError}
            </div>
          )}

          {submitSuccess && (
            <div
              style={{
                padding: '12px',
                backgroundColor: '#e8f5e9',
                color: '#2e7d32',
                borderRadius: '10px',
                marginBottom: '24px',
                fontSize: '14px',
              }}
            >
              {submitSuccess}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '14px',
              backgroundColor: isSubmitting ? '#ccc' : '#e0893f',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s',
            }}
          >
            {isSubmitting ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <span className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></span>
                Processing...
              </span>
            ) : (
              'Submit'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
