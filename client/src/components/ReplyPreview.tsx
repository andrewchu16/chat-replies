"use client";

import { X } from "lucide-react";

interface ReplyPreviewProps {
  messageContent: string;
  onCancel: () => void;
}

export default function ReplyPreview({ messageContent, onCancel }: ReplyPreviewProps) {
  // Truncate the message content to show a preview
  const truncatedContent = messageContent.length > 100 
    ? messageContent.substring(0, 100) + "..." 
    : messageContent;

  return (
    <div className="flex items-center gap-2 p-3 bg-gray-50 border border-gray-200 rounded-lg mb-2">
      <div className="flex-1 min-w-0">
        <div className="text-xs text-gray-500 mb-1">Replying to:</div>
        <div className="text-sm text-gray-700 truncate">
          {truncatedContent}
        </div>
      </div>
      <button
        onClick={onCancel}
        className="flex-shrink-0 p-1 hover:bg-gray-200 rounded-full transition-colors"
        aria-label="Cancel reply"
      >
        <X size={16} className="text-gray-500" />
      </button>
    </div>
  );
}
