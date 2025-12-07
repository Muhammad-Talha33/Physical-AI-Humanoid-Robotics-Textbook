/**
 * ChatWidgetButton Component
 * Floating button to toggle chat widget visibility
 * User Story 1 (T013)
 */

import React from 'react';
import styles from '../../theme/chatStyles.module.css';

export interface ChatWidgetButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export function ChatWidgetButton({ isOpen, onClick }: ChatWidgetButtonProps): JSX.Element {
  return (
    <button
      className={styles.chatWidgetButton}
      onClick={onClick}
      aria-label={isOpen ? 'Close chat widget' : 'Open chat widget'}
      aria-expanded={isOpen}
      aria-controls="chat-widget-container"
      title={isOpen ? 'Close chat' : 'Ask AI about robotics'}
      tabIndex={0}
    >
      {isOpen ? '✕' : '💬'}
    </button>
  );
}

export default ChatWidgetButton;
