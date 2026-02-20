import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

export function Layout({ children }: Props) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100dvh',
        backgroundColor: '#f9fafb',
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      <header
        style={{
          padding: '16px 24px',
          backgroundColor: '#1e3a8a',
          color: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: '20px', fontWeight: 700, letterSpacing: '-0.02em' }}>
          Wenup AI
        </span>
        <span
          style={{
            fontSize: '13px',
            color: '#bfdbfe',
            borderLeft: '1px solid #3b82f6',
            paddingLeft: '12px',
          }}
        >
          Legal Document Preparation
        </span>
      </header>
      {children}
    </div>
  );
}
