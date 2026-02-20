import apiClient from './client';
import type { GenerateResponse, StatusResponse } from '../types';

export async function generateDocument(sessionId: string): Promise<GenerateResponse> {
  const res = await apiClient.post<GenerateResponse>(
    `/sessions/${sessionId}/generate`,
    {},
  );
  return res.data;
}

export async function getGenerationStatus(sessionId: string): Promise<StatusResponse> {
  const res = await apiClient.get<StatusResponse>(`/sessions/${sessionId}/status`);
  return res.data;
}

export function getDownloadUrl(sessionId: string, format: 'pdf' | 'docx'): string {
  return `/api/sessions/${sessionId}/download/${format}`;
}
