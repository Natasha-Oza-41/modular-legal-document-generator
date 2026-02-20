import { useSession } from './hooks/useSession';
import { useSessionStore } from './store/sessionStore';
import { ChatWindow } from './components/chat/ChatWindow';
import { MessageInput } from './components/chat/MessageInput';
import { DocumentReady } from './components/document/DocumentReady';
import { ProgressBar } from './components/document/ProgressBar';
import { Layout } from './components/layout/Layout';

function AppInner() {
  useSession(); // initialises the session on mount

  const { status, error } = useSessionStore();

  return (
    <Layout>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <ProgressBar />
        <ChatWindow />
        {error && (
          <div
            role="alert"
            style={{
              padding: '12px 16px',
              backgroundColor: '#fef2f2',
              borderTop: '1px solid #fecaca',
              color: '#b91c1c',
              fontSize: '14px',
            }}
          >
            {error}
          </div>
        )}
        {(status === 'generating' || status === 'ready') ? (
          <DocumentReady />
        ) : (
          <MessageInput />
        )}
      </div>
    </Layout>
  );
}

export default function App() {
  return <AppInner />;
}
