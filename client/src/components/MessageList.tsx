"use client";

import { ChatMessage } from "../models/chat";
import UserMessage from "./UserMessage";
import AIMessage from "./AIMessage";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  streamingMessageId?: string;
  onReply?: (messageId: string, content: string, replyMetadata?: { startIndex: number; endIndex: number }) => void;
}

export default function MessageList({ messages, isLoading = false, streamingMessageId, onReply }: MessageListProps) {
  return (
    <div className="w-full border border-black/10 rounded-2xl p-4 mb-4 overflow-y-auto">
      <div className="min-h-[40vh] max-h-[60vh] space-y-3">
        {messages.length === 0 ? (
          <p className="text-black/40 text-sm text-center mt-8">
            Your conversation will appear here.
          </p>
        ) : (
          messages.map((message) => (
            <div key={message.id}>
              {message.sender === "user" ? (
                <UserMessage message={message} />
              ) : (
                <AIMessage
                  message={message}
                  isStreaming={streamingMessageId === message.id}
                  isLoading={isLoading}
                  onReply={onReply}
                />
              )}
            </div>
          ))
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
