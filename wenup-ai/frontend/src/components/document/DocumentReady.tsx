import { getDownloadUrl } from '../../api/documents';
import { useSessionStore } from '../../store/sessionStore';

export function DocumentReady() {
  const { sessionId, status } = useSessionStore();

  if (status === 'generating') {
    return (
      <div
        style={{
          padding: '24px',
          textAlign: 'center',
          backgroundColor: '#eff6ff',
          borderTop: '1px solid #bfdbfe',
        }}
        role="status"
      >
        <p style={{ margin: 0, color: '#1e40af', fontWeight: 500 }}>
          Preparing your document, please wait...
        </p>
      </div>
    );
  }

  if (status !== 'ready' || !sessionId) return null;

  const handleDownload = (format: 'pdf' | 'docx') => {
    window.location.href = getDownloadUrl(sessionId, format);
  };

  return (
    <div
      style={{
        padding: '24px',
        backgroundColor: '#f0fdf4',
        borderTop: '1px solid #bbf7d0',
        textAlign: 'center',
      }}
      role="region"
      aria-label="Download your document"
    >
      <h2
        style={{ margin: '0 0 8px', fontSize: '18px', color: '#14532d' }}
      >
        Your document is ready
      </h2>
      <p
        style={{
          margin: '0 0 20px',
          fontSize: '14px',
          color: '#166534',
          maxWidth: '480px',
          marginLeft: 'auto',
          marginRight: 'auto',
        }}
      >
        Please review your document carefully and have it checked by a qualified
        solicitor before signing.
      </p>
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
        <button
          onClick={() => handleDownload('pdf')}
          style={{
            padding: '10px 24px',
            backgroundColor: '#16a34a',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Download PDF
        </button>
        <button
          onClick={() => handleDownload('docx')}
          style={{
            padding: '10px 24px',
            backgroundColor: '#ffffff',
            color: '#16a34a',
            border: '2px solid #16a34a',
            borderRadius: '8px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Download Word (.docx)
        </button>
      </div>
    </div>
  );
}
