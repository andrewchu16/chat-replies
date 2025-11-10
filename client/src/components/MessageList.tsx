"use client";

import { ChatMessage } from "../models/chat";
import UserMessage from "./UserMessage";
import AIMessage from "./AIMessage";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  streamingMessageId?: string;
  onReply?: (messageId: string, content: string, replyMetadata?: { startIndex: number; endIndex: number }) => void;
  onMessageSelect?: (messageId: string) => void;
  selectedMessageId?: string | null;
}

export default function MessageList({ 
  messages, 
  isLoading = false, 
  streamingMessageId, 
  onReply,
  onMessageSelect,
  selectedMessageId 
}: MessageListProps) {
  const handleMessageDoubleClick = (messageId: string, e: React.MouseEvent) => {
    // Don't trigger if user is selecting text
    const selection = window.getSelection();
    if (selection && selection.toString().length > 0) {
      return;
    }
    
    if (onMessageSelect) {
      onMessageSelect(messageId);
    }
  };

  return (
    <div className="w-full border border-black/10 rounded-2xl p-4 mb-4 overflow-y-auto flex-1 min-h-0">
      <div className="space-y-3">
        {messages.length === 0 ? (
          <p className="text-black/40 text-sm text-center mt-8">
            Your conversation will appear here.
          </p>
        ) : (
          messages.map((message) => {
            const isStreaming = streamingMessageId === message.id;
            return (
              <div 
                key={message.id}
                onDoubleClick={(e) => handleMessageDoubleClick(message.id, e)}
                className={`transition-colors rounded-lg p-2 -m-2 select-text ${
                  isStreaming 
                    ? 'opacity-70' 
                    : ''
                } ${selectedMessageId === message.id 
                  ? 'bg-blue-50 border border-blue-200' 
                  : 'hover:bg-gray-50'}`}
              >
                {message.sender === "user" ? (
                  <UserMessage message={message} />
                ) : (
                  <AIMessage
                    message={message}
                    isStreaming={isStreaming}
                    isLoading={isLoading}
                    onReply={onReply}
                  />
                )}
              </div>
            );
          })
        )}
        {isLoading && (
          <div className="w-full p-2">
            <div className="text-sm text-black/40 italic flex items-center gap-2">
              <div className="flex gap-1">
                <div className="w-1 h-1 bg-black/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-1 h-1 bg-black/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-1 h-1 bg-black/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
