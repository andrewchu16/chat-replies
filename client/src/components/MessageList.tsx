"use client";

import ReactMarkdown from "react-markdown";
import { ChatMessage } from "../models/chat";
import ReplyButton from "./ReplyButton";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  streamingMessageId?: string;
  onReply?: (messageId: string, content: string, replyMetadata?: { startIndex: number; endIndex: number }) => void;
}

export default function MessageList({ messages, isLoading = false, streamingMessageId, onReply }: MessageListProps) {
  return (
    <div className="w-full border border-black/10 rounded-2xl p-4 mb-4">
      <div className="min-h-[40vh] max-h-[60vh] overflow-y-auto space-y-3">
        {messages.length === 0 ? (
          <p className="text-black/40 text-sm text-center mt-8">
            Your conversation will appear here.
          </p>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`w-full ${
                message.sender === "user"
                  ? "bg-gray-100 rounded-2xl p-4"
                  : "p-2"
              }`}
            >
              <div className="flex flex-col">
                {message.sender === "user" ? (
                  <div className="text-sm whitespace-pre-wrap">
                    {message.content}
                  </div>
                ) : (
                  <div className="text-sm text-black/70 prose prose-sm max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                    {streamingMessageId === message.id && (
                      <span className="inline-block w-2 h-4 bg-black/70 ml-1 streaming-cursor"></span>
                    )}
                  </div>
                )}
                
                {onReply && message.sender === "assistant" && (
                  <div className="mt-2">
                    <ReplyButton
                      messageId={message.id}
                      messageContent={message.content}
                      onReply={onReply}
                      disabled={isLoading}
                    />
                  </div>
                )}
              </div>
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
