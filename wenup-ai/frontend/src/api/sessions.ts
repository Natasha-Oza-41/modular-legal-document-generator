import apiClient from './client';
import type { CreateSessionResponse } from '../types';

export async function createSession(documentTypeId: string): Promise<CreateSessionResponse> {
  const res = await apiClient.post<CreateSessionResponse>('/sessions', {
    document_type_id: documentTypeId,
  });
  return res.data;
}
