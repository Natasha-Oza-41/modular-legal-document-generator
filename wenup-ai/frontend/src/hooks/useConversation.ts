import { useCallback } from 'react';
import { sendMessage as apiSendMessage } from '../api/conversation';
import { useSessionStore } from '../store/sessionStore';
import { useDocumentGeneration } from './useDocumentGeneration';

/**
 * Handles sending a user message:
 * 1. Adds the user message optimistically
 * 2. Shows typing indicator
 * 3. Calls the API
 * 4. Adds the assistant response
 * 5. If conversation is complete, triggers document generation
 */
export function useConversation() {
  const {
    sessionId,
    addMessage,
    setStatus,
    setProgress,
    setTyping,
    setError,
  } = useSessionStore();

  const { triggerGeneration } = useDocumentGeneration();

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId) return;

      addMessage('user', content);
      setTyping(true);

      try {
        const data = await apiSendMessage(sessionId, content);
        addMessage('assistant', data.response);
        setProgress(data.progress);

        if (data.is_complete) {
          setStatus('complete');
          await triggerGeneration();
        } else {
          setStatus(data.response_type as any);
        }
      } catch {
        setError('Something went wrong sending your message. Please try again.');
      } finally {
        setTyping(false);
      }
    },
    [sessionId, addMessage, setStatus, setProgress, setTyping, setError, triggerGeneration],
  );

  return { sendMessage };
}
