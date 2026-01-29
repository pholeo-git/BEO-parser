import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
  },
});

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
  const formData = new FormData();
  formData.append('name', data.name);
  formData.append('email', data.email);
  if (data.event_name) {
    formData.append('event_name', data.event_name);
  }
  formData.append('pdf_file', data.pdf_file);

  const response = await apiClient.post<UploadResponse>(
    '/api/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${API_KEY}`,
      },
    }
  );

  return response.data;
}

export async function checkStatus(
  submissionId: string
): Promise<SubmissionStatus> {
  const response = await apiClient.get<SubmissionStatus>(
    `/api/status/${submissionId}`,
    {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
      },
    }
  );

  return response.data;
}
