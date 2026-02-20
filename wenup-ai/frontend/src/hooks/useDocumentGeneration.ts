import { generateDocument, getGenerationStatus } from '../api/documents';
import { useSessionStore } from '../store/sessionStore';

const POLL_INTERVAL_MS = 2000;
const MAX_POLLS = 60; // 2 min total

/**
 * Triggers document generation and polls until complete.
 * Updates global store status to 'generating', then 'ready' or 'error'.
 */
export function useDocumentGeneration() {
  const { sessionId, setStatus, setDownloadReady, setError } = useSessionStore();

  async function triggerGeneration() {
    if (!sessionId) return;

    try {
      await generateDocument(sessionId);
      setStatus('generating');
      pollStatus(sessionId);
    } catch {
      setStatus('error');
      setError('Failed to start document generation. Please refresh.');
    }
  }

  function pollStatus(sid: string, attempt = 0) {
    if (attempt >= MAX_POLLS) {
      setStatus('error');
      setError('Document generation timed out. Please try again.');
      return;
    }

    setTimeout(async () => {
      try {
        const data = await getGenerationStatus(sid);
        if (data.status === 'ready') {
          setStatus('ready');
          setDownloadReady(true);
        } else if (data.status === 'error') {
          setStatus('error');
          setError(data.error ?? 'An error occurred during document generation.');
        } else {
          pollStatus(sid, attempt + 1);
        }
      } catch {
        pollStatus(sid, attempt + 1);
      }
    }, POLL_INTERVAL_MS);
  }

  return { triggerGeneration };
}
