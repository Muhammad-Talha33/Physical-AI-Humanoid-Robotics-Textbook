/**
 * Root Component - Global wrapper for all pages
 * Integrates ChatWidget at the root level (client-side only)
 * Alternative to swizzling Layout component
 * User Story 1 (T021-T022)
 */

import React, { useState, useEffect, lazy, Suspense } from 'react';

// Lazy load chat components for better bundle size (T041)
const ChatWidget = lazy(() => import('../components/chat/ChatWidget'));
const ChatWidgetButton = lazy(() => import('../components/chat/ChatWidgetButton'));
const TextSelectionPopover = lazy(() => import('../components/chat/TextSelectionPopover'));

export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isClient, setIsClient] = useState<boolean>(false);
  const [initialQuery, setInitialQuery] = useState<string | undefined>(undefined);
  const [selectedContext, setSelectedContext] = useState<string | undefined>(undefined);

  // Ensure client-side only rendering (T022)
  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleToggle = (): void => {
    setIsOpen(prev => !prev);
  };

  // Handle "Ask AI About This" from text selection (T027, T029)
  const handleAskAIAboutSelection = (selectedText: string): void => {
    // For very short selections, use a more specific prompt
    const isShortSelection = selectedText.length < 100;
    const query = isShortSelection
      ? `What does "${selectedText}" mean in the context of Physical AI and Humanoid Robotics?`
      : `Explain this: "${selectedText}"`;

    setInitialQuery(query);
    setSelectedContext(selectedText);
    setIsOpen(true);
  };

  // Clear initial query when widget closes
  useEffect(() => {
    if (!isOpen) {
      setInitialQuery(undefined);
      setSelectedContext(undefined);
    }
  }, [isOpen]);

  return (
    <>
      {children}
      {isClient && typeof window !== 'undefined' && (
        <Suspense fallback={<div />}>
          <TextSelectionPopover onAskAI={handleAskAIAboutSelection} />
          <ChatWidgetButton isOpen={isOpen} onClick={handleToggle} />
          <ChatWidget
            isOpen={isOpen}
            onClose={() => setIsOpen(false)}
            initialQuery={initialQuery}
            selectedContext={selectedContext}
          />
        </Suspense>
      )}
    </>
  );
}
