/**
 * ChatWidget Component
 * Main chat interface using OpenAI ChatKit
 * User Story 1 (T014-T022)
 */

import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useChatSession } from '../../hooks/useChatSession';
import { sendChatQuery } from '../../services/chatService';
import ErrorBoundary from './ErrorBoundary';
import CitationBadge from './CitationBadge';
import styles from '../../theme/chatStyles.module.css';
import type { Message } from '../../types/chat';

export interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuery?: string;
  selectedContext?: string;
}

export function ChatWidget({ isOpen, onClose, initialQuery, selectedContext }: ChatWidgetProps): JSX.Element {
  const { sessionId, messages, addMessage, clearSession, isReady } = useChatSession();
  const [inputValue, setInputValue] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingContext, setPendingContext] = useState<string | undefined>(undefined);
  const messageListRef = useRef<HTMLDivElement>(null);

  // Handle initial query from text selection (T027)
  useEffect(() => {
    if (initialQuery && isOpen && isReady) {
      setInputValue(initialQuery);
      setPendingContext(selectedContext);
    }
  }, [initialQuery, selectedContext, isOpen, isReady]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  // Handle message submission
  const handleSendMessage = async (): Promise<void> => {
    const query = inputValue.trim();

    // Validate input
    if (!query || query.length === 0) {
      return;
    }

    if (query.length > 1000) {
      setError('Message is too long (max 1000 characters)');
      return;
    }

    // Clear input and error
    setInputValue('');
    setError(null);

    // Add user message to conversation
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: query,
      timestamp: new Date(),
    };
    addMessage(userMessage);

    // Send query to backend (T028 - include selected_context parameter)
    setIsLoading(true);
    try {
      const response = await sendChatQuery(query, sessionId, pendingContext);

      // Clear pending context after sending
      setPendingContext(undefined);

      // Add assistant response to conversation
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        citations: response.citations,
      };
      addMessage(assistantMessage);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Add error message to conversation for user visibility
      const errorMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date(),
      };
      addMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press (Shift+Enter for new line)
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle clear conversation
  const handleClearConversation = (): void => {
    if (window.confirm('Are you sure you want to clear the conversation?')) {
      clearSession();
      setError(null);
    }
  };

  // Don't render until session is ready
  if (!isReady) {
    return <></>;
  }

  return (
    <ErrorBoundary>
      <div id="chat-widget-container" className={`${styles.chatWidget} ${!isOpen ? styles.hidden : ''}`} role="dialog" aria-label="Chat with AI assistant">
        {/* Header */}
        <div className={styles.chatHeader}>
          <h3 className={styles.chatTitle}>💬 Ask AI about Robotics</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className={styles.closeButton}
              onClick={handleClearConversation}
              aria-label="Clear conversation"
              title="Clear conversation"
              style={{ fontSize: '16px' }}
            >
              🗑️
            </button>
            <button
              className={styles.closeButton}
              onClick={onClose}
              aria-label="Close chat"
              title="Close chat"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Message List */}
        <div className={styles.messageList} ref={messageListRef} role="log" aria-live="polite" aria-label="Chat messages">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--chat-widget-text-secondary)', padding: '20px' }}>
              <p>👋 Welcome! Ask me anything about Physical AI and Humanoid Robotics.</p>
              <p style={{ fontSize: '12px', marginTop: '10px' }}>
                <strong>Tips for best results:</strong><br/>
                • Ask specific questions: "What is ROS 2?"<br/>
                • Highlight text and click "Ask AI About This"<br/>
                • Select full paragraphs for detailed explanations
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`${styles.message} ${styles[message.role]}`}>
              <div className={styles.messageContent}>
                {message.content}
                {message.citations && message.citations.length > 0 && (
                  <div style={{ marginTop: '8px' }}>
                    {message.citations.map((citation, index) => (
                      <CitationBadge key={index} citation={citation} index={index} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className={styles.message} style={{ alignSelf: 'flex-start' }}>
              <div className={styles.loadingIndicator}>
                <div className={styles.loadingDot}></div>
                <div className={styles.loadingDot}></div>
                <div className={styles.loadingDot}></div>
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div
            style={{
              padding: '12px 16px',
              backgroundColor: 'var(--ifm-alert-background-color, #f8d7da)',
              borderTop: '1px solid var(--ifm-alert-border-color, #f5c6cb)',
              color: 'var(--ifm-alert-foreground-color, #721c24)',
              fontSize: '13px',
            }}
          >
            <strong>Error:</strong> {error}
            <button
              onClick={() => setError(null)}
              style={{
                marginLeft: '10px',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontSize: '16px',
              }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Input Composer */}
        <div className={styles.composer}>
          <textarea
            className={styles.input}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your question... (Shift+Enter for new line)"
            rows={1}
            disabled={isLoading}
            maxLength={1000}
            aria-label="Chat message input"
            aria-describedby="chat-input-help"
          />
          <span id="chat-input-help" style={{ display: 'none' }}>
            Enter your question about Physical AI and Humanoid Robotics. Press Enter to send, Shift+Enter for new line.
          </span>
          <button
            className={styles.sendButton}
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            aria-label="Send message"
          >
            {isLoading ? '...' : '➤'}
          </button>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default ChatWidget;
