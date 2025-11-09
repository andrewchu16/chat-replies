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
  const handleMessageClick = (messageId: string) => {
    // Don't allow selecting messages that are currently streaming
    if (streamingMessageId === messageId) {
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
                onClick={() => handleMessageClick(message.id)}
                className={`transition-colors rounded-lg p-2 -m-2 ${
                  isStreaming 
                    ? 'cursor-not-allowed opacity-70' 
                    : 'cursor-pointer ' + (selectedMessageId === message.id 
                      ? 'bg-blue-50 border border-blue-200' 
                      : 'hover:bg-gray-50')
                }`}
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
              AI is typing...
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
