import { type KeyboardEvent, useCallback, useState } from 'react';
import { useConversation } from '../../hooks/useConversation';
import { useSessionStore } from '../../store/sessionStore';

export function MessageInput() {
  const [value, setValue] = useState('');
  const { sendMessage } = useConversation();
  const { status, isTyping, sessionId } = useSessionStore();

  const isDisabled =
    !sessionId ||
    isTyping ||
    status === 'complete' ||
    status === 'generating' ||
    status === 'ready' ||
    status === 'error' ||
    status === 'initialising';

  const handleSend = useCallback(async () => {
    const trimmed = value.trim();
    if (!trimmed || isDisabled) return;
    setValue('');
    await sendMessage(trimmed);
  }, [value, isDisabled, sendMessage]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const placeholder = isTyping
    ? 'Please wait...'
    : isDisabled
      ? ''
      : 'Type your answer and press Enter...';

  return (
    <div
      style={{
        display: 'flex',
        gap: '8px',
        padding: '12px 16px',
        borderTop: '1px solid #e5e7eb',
        backgroundColor: '#ffffff',
      }}
    >
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isDisabled}
        placeholder={placeholder}
        rows={2}
        aria-label="Your message"
        style={{
          flex: 1,
          resize: 'none',
          borderRadius: '8px',
          border: '1px solid #d1d5db',
          padding: '10px 12px',
          fontSize: '15px',
          fontFamily: 'inherit',
          outline: 'none',
          lineHeight: '1.5',
          backgroundColor: isDisabled ? '#f9fafb' : '#ffffff',
          color: '#111827',
        }}
      />
      <button
        onClick={handleSend}
        disabled={isDisabled || !value.trim()}
        aria-label="Send message"
        style={{
          padding: '0 20px',
          borderRadius: '8px',
          border: 'none',
          backgroundColor:
            isDisabled || !value.trim() ? '#d1d5db' : '#1a56db',
          color: '#ffffff',
          fontSize: '15px',
          fontWeight: 600,
          cursor: isDisabled || !value.trim() ? 'not-allowed' : 'pointer',
          transition: 'background-color 0.15s',
          minWidth: '80px',
        }}
      >
        Send
      </button>
    </div>
  );
}
