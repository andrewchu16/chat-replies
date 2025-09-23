"use client";

interface ReplyButtonProps {
  messageId: string;
  messageContent: string;
  onReply: (messageId: string, messageContent: string, replyMetadata?: { startIndex: number; endIndex: number }) => void;
  disabled?: boolean;
}

export default function ReplyButton({ 
  messageId, 
  messageContent, 
  onReply, 
  disabled = false 
}: ReplyButtonProps) {
  const handleReply = () => {
    onReply(messageId, messageContent);
  };

  return (
    <button
      onClick={handleReply}
      disabled={disabled}
      className="text-xs text-gray-500 hover:text-gray-700 disabled:opacity-50"
    >
      Reply
    </button>
  );
}
