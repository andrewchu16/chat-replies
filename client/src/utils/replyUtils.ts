/**
 * Utility functions for handling message replies
 */

export interface TextSelection {
  text: string;
  startIndex: number;
  endIndex: number;
}

/**
 * Get the selected text and its position within a message
 */
export function getTextSelection(element: HTMLElement): TextSelection | null {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) {
    return null;
  }

  const range = selection.getRangeAt(0);
  const selectedText = range.toString().trim();
  
  if (!selectedText) {
    return null;
  }

  // Find the start and end positions within the element
  const preSelectionRange = range.cloneRange();
  preSelectionRange.selectNodeContents(element);
  preSelectionRange.setEnd(range.startContainer, range.startOffset);
  
  const startIndex = preSelectionRange.toString().length;
  const endIndex = startIndex + selectedText.length;

  return {
    text: selectedText,
    startIndex,
    endIndex,
  };
}

/**
 * Validate reply metadata
 */
export function validateReplyMetadata(
  startIndex: number,
  endIndex: number,
  messageLength: number
): boolean {
  return (
    startIndex >= 0 &&
    endIndex > startIndex &&
    endIndex <= messageLength
  );
}

/**
 * Extract reply metadata from a formatted reply message
 */
export function extractReplyMetadata(replyContent: string): {
  content: string;
  replyMetadata?: { startIndex: number; endIndex: number };
} {
  // Look for quoted text in the format: > "selected text"
  const quoteMatch = replyContent.match(/>\s*"([^"]+)"/);
  
  if (quoteMatch) {
    const quotedText = quoteMatch[1];
    const content = replyContent.replace(/>\s*"[^"]+"/, '').trim();
    
    return {
      content,
      replyMetadata: {
        startIndex: 0, // This would need to be calculated based on the original message
        endIndex: quotedText.length,
      },
    };
  }

  return {
    content: replyContent,
  };
}
