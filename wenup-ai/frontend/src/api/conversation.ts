import apiClient from './client';
import type { MessageResponse } from '../types';

export async function sendMessage(
  sessionId: string,
  message: string,
): Promise<MessageResponse> {
  const res = await apiClient.post<MessageResponse>(
    `/sessions/${sessionId}/message`,
    { message },
  );
  return res.data;
}
