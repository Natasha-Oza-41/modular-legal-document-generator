import { create } from 'zustand';
import type { Message, MessageRole, SessionStatus } from '../types';

interface SessionState {
  sessionId: string | null;
  documentTypeId: string;
  status: SessionStatus;
  messages: Message[];
  progress: number;
  isTyping: boolean;
  downloadReady: boolean;
  error: string | null;

  // Actions
  setSessionId: (id: string) => void;
  addMessage: (role: MessageRole, content: string) => void;
  setStatus: (status: SessionStatus) => void;
  setProgress: (progress: number) => void;
  setTyping: (typing: boolean) => void;
  setDownloadReady: (ready: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  sessionId: null,
  documentTypeId: 'will_england_wales',
  status: 'initialising' as SessionStatus,
  messages: [] as Message[],
  progress: 0,
  isTyping: false,
  downloadReady: false,
  error: null,
};

export const useSessionStore = create<SessionState>((set) => ({
  ...initialState,

  setSessionId: (id) => set({ sessionId: id }),

  addMessage: (role, content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          role,
          content,
          timestamp: new Date(),
        },
      ],
    })),

  setStatus: (status) => set({ status }),
  setProgress: (progress) => set({ progress }),
  setTyping: (isTyping) => set({ isTyping }),
  setDownloadReady: (downloadReady) => set({ downloadReady }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
