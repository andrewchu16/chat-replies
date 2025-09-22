"use client";

import { useState } from "react";

interface ReplyButtonProps {
  messageId: string;
  messageContent: string;
  onReply: (messageId: string, content: string, replyMetadata?: { startIndex: number; endIndex: number }) => void;
  disabled?: boolean;
}

export default function ReplyButton({ 
  messageId, 
  messageContent, 
  onReply, 
  disabled = false 
}: ReplyButtonProps) {
  const [isReplying, setIsReplying] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [selectedText, setSelectedText] = useState<{ text: string; startIndex: number; endIndex: number } | null>(null);

  const handleReply = () => {
    if (!replyText.trim()) return;

    onReply(
      messageId, 
      replyText, 
      selectedText ? {
        startIndex: selectedText.startIndex,
        endIndex: selectedText.endIndex,
      } : undefined
    );

    // Reset form
    setReplyText("");
    setSelectedText(null);
    setIsReplying(false);
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      const selectedText = selection.toString().trim();
      // For simplicity, we'll use the selected text as the reply metadata
      // In a real implementation, you'd calculate the actual indices
      setSelectedText({
        text: selectedText,
        startIndex: 0,
        endIndex: selectedText.length,
      });
    }
  };

  if (!isReplying) {
    return (
      <button
        onClick={() => setIsReplying(true)}
        disabled={disabled}
        className="text-xs text-gray-500 hover:text-gray-700 disabled:opacity-50"
      >
        Reply
      </button>
    );
  }

  return (
    <div className="mt-2 p-3 bg-gray-50 rounded-lg border">
      <div className="mb-2">
        <label className="block text-xs font-medium text-gray-700 mb-1">
          Reply to message:
        </label>
        <div className="text-xs text-gray-600 bg-white p-2 rounded border max-h-20 overflow-y-auto">
          {messageContent}
        </div>
      </div>
      
      <div className="mb-2">
        <label className="block text-xs font-medium text-gray-700 mb-1">
          Your reply:
        </label>
        <textarea
          value={replyText}
          onChange={(e) => setReplyText(e.target.value)}
          placeholder="Type your reply..."
          className="w-full text-sm p-2 border rounded resize-none"
          rows={2}
        />
      </div>

      {selectedText && (
        <div className="mb-2">
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Selected text:
          </label>
          <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded border">
            &quot;{selectedText.text}&quot;
          </div>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={handleReply}
          disabled={!replyText.trim()}
          className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Send Reply
        </button>
        <button
          onClick={() => {
            setIsReplying(false);
            setReplyText("");
            setSelectedText(null);
          }}
          className="px-3 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
        >
          Cancel
        </button>
        <button
          onClick={handleTextSelection}
          className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
        >
          Select Text
        </button>
      </div>
    </div>
  );
}
