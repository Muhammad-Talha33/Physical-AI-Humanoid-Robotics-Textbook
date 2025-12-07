/**
 * CitationBadge Component
 * Displays citation with chapter/section and optional link
 * User Story 3 (T031)
 */

import React from 'react';
import styles from '../../theme/chatStyles.module.css';
import type { Citation } from '../../types/chat';

export interface CitationBadgeProps {
  citation: Citation;
  index?: number;
}

export function CitationBadge({ citation, index }: CitationBadgeProps): JSX.Element {
  const { chapter, section, url } = citation;

  // If URL is provided, make citation clickable (T034)
  if (url) {
    return (
      <a
        href={url}
        className={styles.citationBadge}
        target="_blank"
        rel="noopener noreferrer"
        title={`${chapter} - ${section}`}
      >
        📚 {chapter} - {section}
      </a>
    );
  }

  // Non-clickable citation badge
  return (
    <span className={styles.citationBadge} title={`${chapter} - ${section}`}>
      📚 {chapter} - {section}
    </span>
  );
}

export default CitationBadge;
