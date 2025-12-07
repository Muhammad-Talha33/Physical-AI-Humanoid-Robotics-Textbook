/**
 * useTextSelection Hook
 * Detects text selection using window.getSelection() API
 * User Story 2 (T023)
 */

import { useState, useEffect, useCallback } from 'react';
import type { SelectedContext } from '../types/chat';

export interface UseTextSelectionReturn {
  selectedText: string;
  selectionRect: DOMRect | null;
  hasSelection: boolean;
  clearSelection: () => void;
}

/**
 * Hook for detecting and managing text selection
 *
 * @returns Selected text, bounding rectangle, and helper functions
 */
export function useTextSelection(): UseTextSelectionReturn {
  const [selectedText, setSelectedText] = useState<string>('');
  const [selectionRect, setSelectionRect] = useState<DOMRect | null>(null);

  /**
   * Handle text selection changes
   */
  const handleSelectionChange = useCallback((): void => {
    const selection = window.getSelection();

    if (!selection || selection.rangeCount === 0) {
      setSelectedText('');
      setSelectionRect(null);
      return;
    }

    const text = selection.toString().trim();

    // Only process selections with meaningful text (min 20 chars to ensure enough context)
    // This prevents short title selections that don't provide enough context for the RAG system
    if (text.length < 20) {
      setSelectedText('');
      setSelectionRect(null);
      return;
    }

    // Get bounding rectangle of selection
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    // Only update if we have a valid rectangle
    if (rect.width > 0 && rect.height > 0) {
      setSelectedText(text);
      setSelectionRect(rect);
    } else {
      setSelectedText('');
      setSelectionRect(null);
    }
  }, []);

  /**
   * Handle mouseup events to detect selection
   */
  const handleMouseUp = useCallback((): void => {
    // Small delay to ensure selection is finalized
    setTimeout(handleSelectionChange, 50);
  }, [handleSelectionChange]);

  /**
   * Clear current selection
   */
  const clearSelection = useCallback((): void => {
    const selection = window.getSelection();
    if (selection) {
      selection.removeAllRanges();
    }
    setSelectedText('');
    setSelectionRect(null);
  }, []);

  // Set up event listeners
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    // Listen for mouseup events to detect selection
    document.addEventListener('mouseup', handleMouseUp);

    // Listen for selection changes (works for keyboard selection too)
    document.addEventListener('selectionchange', handleSelectionChange);

    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, [handleMouseUp, handleSelectionChange]);

  return {
    selectedText,
    selectionRect,
    hasSelection: selectedText.length > 0 && selectionRect !== null,
    clearSelection,
  };
}
