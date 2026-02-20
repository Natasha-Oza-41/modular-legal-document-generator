import { useEffect } from 'react';
import { createSession } from '../api/sessions';
import { useSessionStore } from '../store/sessionStore';

/**
 * Initialises an anonymous session on mount.
 * The opening message from the backend is added to the message list.
 */
export function useSession() {
  const { documentTypeId, setSessionId, addMessage, setStatus, setError } =
    useSessionStore();

  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        const data = await createSession(documentTypeId);
        if (cancelled) return;
        setSessionId(data.session_id);
        addMessage('assistant', data.opening_message);
        setStatus('collecting');
      } catch {
        if (!cancelled) {
          setError('Failed to connect to the server. Please refresh the page.');
          setStatus('error');
        }
      }
    }

    init();
    return () => {
      cancelled = true;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
}
