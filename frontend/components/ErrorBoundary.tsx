'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            backgroundColor: '#fffaf0',
          }}
        >
          <div
            style={{
              maxWidth: '600px',
              backgroundColor: 'white',
              padding: '40px',
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            }}
          >
            <h1 style={{ color: '#d32f2f', marginBottom: '16px' }}>
              Something went wrong
            </h1>
            <p style={{ color: '#3f4040', marginBottom: '24px' }}>
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              style={{
                padding: '12px 24px',
                backgroundColor: '#e0893f',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer',
              }}
            >
              Reload Page
            </button>
            {this.state.error && (
              <details style={{ marginTop: '24px' }}>
                <summary style={{ cursor: 'pointer', color: '#666' }}>
                  Error Details
                </summary>
                <pre
                  style={{
                    marginTop: '12px',
                    padding: '12px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '8px',
                    overflow: 'auto',
                    fontSize: '12px',
                  }}
                >
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
