import { useSessionStore } from '../../store/sessionStore';

export function ProgressBar() {
  const { progress, status } = useSessionStore();

  const displayProgress =
    status === 'ready' || status === 'generating' ? 100 : progress;

  return (
    <div
      style={{ padding: '0 16px 12px' }}
      aria-label={`Conversation progress: ${displayProgress}%`}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: '#6b7280',
          marginBottom: '4px',
        }}
      >
        <span>Progress</span>
        <span>{displayProgress}%</span>
      </div>
      <div
        style={{
          height: '6px',
          backgroundColor: '#e5e7eb',
          borderRadius: '3px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${displayProgress}%`,
            backgroundColor: displayProgress === 100 ? '#059669' : '#1a56db',
            borderRadius: '3px',
            transition: 'width 0.5s ease, background-color 0.3s',
          }}
        />
      </div>
    </div>
  );
}
