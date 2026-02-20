export type MessageRole = 'user' | 'assistant';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
}

export type SessionStatus =
  | 'initialising'
  | 'greeting'
  | 'collecting'
  | 'clarifying'
  | 'redirect'
  | 'injection'
  | 'complete'
  | 'generating'
  | 'ready'
  | 'error';

export interface CreateSessionResponse {
  session_id: string;
  document_type_id: string;
  status: string;
  opening_message: string;
  progress: number;
}

export interface MessageResponse {
  session_id: string;
  response: string;
  response_type: string;
  progress: number;
  is_complete: boolean;
}

export interface GenerateResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface StatusResponse {
  session_id: string;
  status: string;
  error: string | null;
}

export interface DocumentType {
  document_type_id: string;
  display_name: string;
  jurisdiction: string;
}
