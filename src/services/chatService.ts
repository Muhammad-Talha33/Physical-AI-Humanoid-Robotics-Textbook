/**
 * Chat Service - Backend communication with retry logic
 * Based on plan.md research decision #4 (Backend Communication)
 */

import type { ChatQueryRequest, ChatQueryResponse, ChatErrorResponse } from '../types/chat';

/**
 * Get backend URL from Docusaurus custom fields
 * Falls back to hardcoded URL if window.docusaurus is not available
 */
function getBackendUrl(): string {
  // Try to access Docusaurus site config from window object
  const siteConfig = (window as any)?.docusaurus?.siteConfig;
  const backendUrl = siteConfig?.customFields?.chatBackendUrl;

  if (backendUrl) {
    return backendUrl as string;
  }

  // Fallback: Use environment variable or hardcoded backend URL
  const fallbackUrl = 'https://physical-ai-humanoid-robotics-textbook-production-3516.up.railway.app';

  console.warn('Using fallback backend URL. Docusaurus customFields not available.');
  return fallbackUrl;
}

/**
 * Exponential backoff delay calculation
 */
function getBackoffDelay(attemptNumber: number): number {
  // Base delay: 1 second, multiplied by 2^attemptNumber
  // Attempt 1: 2s, Attempt 2: 4s, Attempt 3: 8s
  return 1000 * Math.pow(2, attemptNumber);
}

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Send chat query to RAG backend with retry logic
 *
 * @param query - User's question (1-1000 chars)
 * @param sessionId - UUID v4 session identifier
 * @param selectedContext - Optional highlighted text (max 2000 chars)
 * @returns Promise resolving to ChatQueryResponse
 * @throws Error if all retry attempts fail
 */
export async function sendChatQuery(
  query: string,
  sessionId: string,
  selectedContext?: string
): Promise<ChatQueryResponse> {
  const backendUrl = getBackendUrl();
  const maxRetries = 3;
  let lastError: Error | null = null;

  // Validate input
  if (!query || query.trim().length === 0) {
    throw new Error('Query cannot be empty');
  }
  if (query.length > 1000) {
    throw new Error('Query exceeds maximum length of 1000 characters');
  }
  if (selectedContext && selectedContext.length > 2000) {
    throw new Error('Selected context exceeds maximum length of 2000 characters');
  }

  // Prepare request body
  const requestBody: ChatQueryRequest = {
    query: query.trim(),
    sessionId,
  };

  if (selectedContext && selectedContext.trim().length > 0) {
    requestBody.selected_context = selectedContext.trim();
  }

  // Retry loop with exponential backoff
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(`${backendUrl}/api/v1/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      // Handle non-2xx responses
      if (!response.ok) {
        let errorMessage = `Backend error: ${response.status}`;

        try {
          const errorData: ChatErrorResponse = await response.json();
          errorMessage = errorData.error || errorMessage;
        } catch {
          // If error response isn't JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }

        // Don't retry on 4xx client errors (bad request, invalid input)
        if (response.status >= 400 && response.status < 500) {
          throw new Error(errorMessage);
        }

        // Retry on 5xx server errors
        lastError = new Error(errorMessage);

        if (attempt < maxRetries - 1) {
          const delay = getBackoffDelay(attempt);
          console.warn(`Chat query failed (attempt ${attempt + 1}/${maxRetries}), retrying in ${delay}ms...`);
          await sleep(delay);
          continue;
        }
      } else {
        // Success - parse and return response
        const data = await response.json();

        // Backend returns { response: string, citations: [...] }
        // We need to transform to { answer: string, citations: [...] }
        const transformedData: ChatQueryResponse = {
          answer: data.response || data.answer || '',
          citations: data.citations || [],
        };

        // Validate response structure
        if (!transformedData.answer || typeof transformedData.answer !== 'string') {
          throw new Error('Invalid response format: missing or invalid response field');
        }

        return transformedData;
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error occurred');

      // Don't retry on network errors or parsing errors on last attempt
      if (attempt === maxRetries - 1) {
        break;
      }

      // Retry on network errors
      const delay = getBackoffDelay(attempt);
      console.warn(`Chat query failed (attempt ${attempt + 1}/${maxRetries}), retrying in ${delay}ms...`, error);
      await sleep(delay);
    }
  }

  // All retries exhausted
  throw new Error(
    `Failed to send chat query after ${maxRetries} attempts: ${lastError?.message || 'Unknown error'}`
  );
}
