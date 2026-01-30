import axios from 'axios';

// Safely get environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

// Log for debugging (will show in browser console)
if (typeof window !== 'undefined') {
  console.log('API Configuration:', {
    API_URL,
    API_KEY_SET: !!API_KEY,
    API_KEY_LENGTH: API_KEY?.length || 0,
    ENV_CHECK: {
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NEXT_PUBLIC_API_KEY: process.env.NEXT_PUBLIC_API_KEY ? 'SET' : 'NOT SET',
    },
  });
  
  // Validate configuration
  if (!API_URL || API_URL === 'http://localhost:8000') {
    console.warn('NEXT_PUBLIC_API_URL may not be set correctly!', {
      actual: API_URL,
      env: process.env.NEXT_PUBLIC_API_URL,
    });
  }
  if (!API_KEY) {
    console.warn('NEXT_PUBLIC_API_KEY is not set!');
  }
}

// Create axios client with error handling
let apiClient: ReturnType<typeof axios.create>;

try {
  apiClient = axios.create({
    baseURL: API_URL || 'http://localhost:8000',
  });

  // Add auth header only if API_KEY is set
  if (API_KEY) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${API_KEY}`;
  }
} catch (error) {
  console.error('Failed to create API client:', error);
  // Fallback: create a minimal client
  apiClient = axios.create({
    baseURL: 'http://localhost:8000',
  });
}

export interface UploadSubmissionData {
  name: string;
  email: string;
  event_name?: string;
  pdf_file: File;
}

export interface UploadResponse {
  submission_id: string;
  status: string;
  status_url: string;
  message: string;
}

export interface SubmissionStatus {
  id: string;
  name: string;
  email: string;
  event_name?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  download_url?: string;
  error_message?: string;
  file_size?: number;
  beo_count?: number;
}

export async function uploadSubmission(
  data: UploadSubmissionData
): Promise<UploadResponse> {
  try {
    if (!API_URL) {
      throw new Error('API URL is not configured. Please set NEXT_PUBLIC_API_URL.');
    }
    if (!API_KEY) {
      throw new Error('API Key is not configured. Please set NEXT_PUBLIC_API_KEY.');
    }

    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('email', data.email);
    if (data.event_name) {
      formData.append('event_name', data.event_name);
    }
    formData.append('pdf_file', data.pdf_file);

    console.log('Uploading to:', API_URL);
    console.log('API Key set:', !!API_KEY);

    const headers: Record<string, string> = {
      'Authorization': `Bearer ${API_KEY}`,
      // Don't set Content-Type - let axios set it with boundary for multipart/form-data
    };

    const response = await apiClient.post<UploadResponse>(
      '/api/upload',
      formData,
      {
        headers,
        timeout: 60000, // 60 second timeout for large files
      }
    );

    return response.data;
  } catch (error: any) {
    console.error('Upload submission error:', error);
    throw error;
  }
}

export async function checkStatus(
  submissionId: string
): Promise<SubmissionStatus> {
  try {
    if (!API_URL) {
      throw new Error('API URL is not configured. Please set NEXT_PUBLIC_API_URL.');
    }
    if (!API_KEY) {
      throw new Error('API Key is not configured. Please set NEXT_PUBLIC_API_KEY.');
    }

    const response = await apiClient.get<SubmissionStatus>(
      `/api/status/${submissionId}`,
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  } catch (error: any) {
    console.error('Check status error:', error);
    throw error;
  }
}
