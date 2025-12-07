/**
 * useChatSession Hook
 * Manages chat session ID generation and localStorage persistence
 * Based on plan.md research decision #3 (Session Management)
 */

import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import type { Message, StoredSession } from '../types/chat';

const STORAGE_KEY = 'chatbot-session';

/**
 * Parse stored session from localStorage
 */
function loadStoredSession(): StoredSession | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    const parsed: StoredSession = JSON.parse(stored);

    // Validate structure
    if (!parsed.sessionId || !Array.isArray(parsed.messages)) {
      console.warn('Invalid stored session structure, ignoring');
      return null;
    }

    return parsed;
  } catch (error) {
    console.error('Failed to load stored session:', error);
    return null;
  }
}

/**
 * Save session to localStorage
 */
function saveSession(sessionId: string, messages: Message[]): void {
  try {
    const now = new Date().toISOString();
    const storedSession: StoredSession = {
      sessionId,
      messages: messages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp.toISOString(),
        citations: msg.citations,
      })),
      createdAt: now,
      lastActivityAt: now,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(storedSession));
  } catch (error) {
    console.error('Failed to save session:', error);
  }
}

/**
 * Convert stored messages back to Message objects
 */
function hydrateMessages(stored: StoredSession): Message[] {
  return stored.messages.map(msg => ({
    ...msg,
    timestamp: new Date(msg.timestamp),
  }));
}

export interface UseChatSessionReturn {
  sessionId: string;
  messages: Message[];
  addMessage: (message: Message) => void;
  clearSession: () => void;
  isReady: boolean;
}

/**
 * Hook for managing chat session state with localStorage persistence
 *
 * @returns Session ID, messages array, and helper functions
 */
export function useChatSession(): UseChatSessionReturn {
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isReady, setIsReady] = useState<boolean>(false);

  // Initialize session on mount
  useEffect(() => {
    const stored = loadStoredSession();

    if (stored) {
      // Restore existing session
      setSessionId(stored.sessionId);
      setMessages(hydrateMessages(stored));
    } else {
      // Create new session
      const newSessionId = uuidv4();
      setSessionId(newSessionId);
      setMessages([]);
      saveSession(newSessionId, []);
    }

    setIsReady(true);
  }, []);

  // Persist messages whenever they change
  useEffect(() => {
    if (isReady && sessionId) {
      saveSession(sessionId, messages);
    }
  }, [messages, sessionId, isReady]);

  /**
   * Add a new message to the conversation
   */
  const addMessage = (message: Message): void => {
    setMessages(prev => [...prev, message]);
  };

  /**
   * Clear current session and start fresh
   */
  const clearSession = (): void => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    saveSession(newSessionId, []);
  };

  return {
    sessionId,
    messages,
    addMessage,
    clearSession,
    isReady,
  };
}
