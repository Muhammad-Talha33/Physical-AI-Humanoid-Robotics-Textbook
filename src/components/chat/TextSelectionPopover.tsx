/**
 * TextSelectionPopover Component
 * Displays "Ask AI About This" button near selected text
 * User Story 2 (T024)
 */

import React, { useEffect, useState } from 'react';
import { useTextSelection } from '../../hooks/useTextSelection';
import styles from '../../theme/chatStyles.module.css';

export interface TextSelectionPopoverProps {
  onAskAI: (selectedText: string) => void;
}

export function TextSelectionPopover({ onAskAI }: TextSelectionPopoverProps): JSX.Element | null {
  const { selectedText, selectionRect, hasSelection, clearSelection } = useTextSelection();
  const [popoverPosition, setPopoverPosition] = useState<{ top: number; left: number } | null>(null);

  // Calculate popover position from selection bounding box (T026)
  useEffect(() => {
    if (!hasSelection || !selectionRect) {
      setPopoverPosition(null);
      return;
    }

    // Position popover above the selection, centered
    const top = selectionRect.top + window.scrollY - 45; // 45px above selection
    const left = selectionRect.left + window.scrollX + selectionRect.width / 2 - 75; // Center (button width ~150px)

    // Ensure popover stays within viewport
    const adjustedLeft = Math.max(10, Math.min(left, window.innerWidth - 160));

    setPopoverPosition({
      top: Math.max(10, top), // Don't go above viewport
      left: adjustedLeft,
    });
  }, [hasSelection, selectionRect]);

  /**
   * Handle "Ask AI About This" button click (T027, T030)
   */
  const handleAskAI = (): void => {
    if (!selectedText) return;

    // Pass selected text to parent component (T027)
    onAskAI(selectedText);

    // Clear selection and hide popover (T030)
    clearSelection();
  };

  // Don't render if no selection
  if (!hasSelection || !popoverPosition) {
    return null;
  }

  return (
    <div
      className={styles.textSelectionPopover}
      style={{
        position: 'absolute',
        top: `${popoverPosition.top}px`,
        left: `${popoverPosition.left}px`,
        zIndex: 10000,
      }}
    >
      <button className={styles.askAIButton} onClick={handleAskAI} title="Ask AI about this selection">
        💡 Ask AI About This
      </button>
    </div>
  );
}

export default TextSelectionPopover;
