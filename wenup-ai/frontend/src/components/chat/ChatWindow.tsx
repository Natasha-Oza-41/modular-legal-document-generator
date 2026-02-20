import { useEffect, useRef } from 'react';
import { useSessionStore } from '../../store/sessionStore';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';

export function ChatWindow() {
  const { messages, isTyping } = useSessionStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div
      aria-live="polite"
      aria-label="Conversation"
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px 16px 8px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {isTyping && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
}
