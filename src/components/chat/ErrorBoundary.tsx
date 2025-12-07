/**
 * ErrorBoundary Component
 * Catches React errors in chat widget and displays fallback UI
 * Based on plan.md research decision #5 (Error Handling)
 */

import React, { Component, ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render shows the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error to console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div
          style={{
            padding: '20px',
            backgroundColor: 'var(--ifm-alert-background-color, #f8d7da)',
            border: '1px solid var(--ifm-alert-border-color, #f5c6cb)',
            borderRadius: '4px',
            color: 'var(--ifm-alert-foreground-color, #721c24)',
          }}
        >
          <h3 style={{ marginTop: 0 }}>Something went wrong</h3>
          <p>The chat widget encountered an error. Please try again.</p>
          {this.state.error && (
            <details style={{ marginTop: '10px' }}>
              <summary style={{ cursor: 'pointer' }}>Error details</summary>
              <pre
                style={{
                  marginTop: '10px',
                  padding: '10px',
                  backgroundColor: 'rgba(0, 0, 0, 0.05)',
                  borderRadius: '4px',
                  fontSize: '12px',
                  overflow: 'auto',
                }}
              >
                {this.state.error.toString()}
              </pre>
            </details>
          )}
          <button
            onClick={this.handleReset}
            style={{
              marginTop: '15px',
              padding: '8px 16px',
              backgroundColor: 'var(--ifm-color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
