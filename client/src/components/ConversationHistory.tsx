"use client";

import { ChatMessage } from "../models/chat";

interface ConversationHistoryProps {
  messages: ChatMessage[];
}

function truncateContent(content: string, maxLength: number = 150): string {
  if (content.length <= maxLength) {
    return content;
  }
  return content.substring(0, maxLength) + "...";
}

function CompactMessage({ message }: { message: ChatMessage }) {
  const isUser = message.sender === "user";

  return (
    <div
      className={`flex gap-2 text-xs ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`px-2.5 py-1.5 rounded-lg max-w-[85%] ${
          isUser ? "bg-blue-500 text-white" : "bg-black/5 text-black/80"
        }`}
      >
        <div className="flex items-center gap-1.5 mb-0.5">
          <span
            className={`font-medium ${
              isUser ? "text-blue-100" : "text-black/60"
            }`}
          >
            {isUser ? "User" : "AI"}
          </span>
          {message.timestamp && (
            <span
              className={`text-[10px] ${
                isUser ? "text-blue-200" : "text-black/40"
              }`}
            >
              {message.timestamp.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          )}
        </div>
        <div
          className={`leading-relaxed whitespace-pre-wrap break-words ${
            isUser ? "text-white/95" : "text-black/70"
          }`}
        >
          {truncateContent(message.content)}
        </div>
      </div>
    </div>
  );
}

export default function ConversationHistory({
  messages,
}: ConversationHistoryProps) {
  return (
    <div className="w-full h-full border border-black/10 rounded-2xl p-4 overflow-y-auto flex flex-col min-h-0">
      <div className="mb-3 pb-2 border-b border-black/10">
        <h2 className="text-base font-semibold text-black">
          Conversation History
        </h2>
        <p className="text-[11px] text-black/50 mt-0.5">
          {messages.length} message{messages.length !== 1 ? "s" : ""}
        </p>
      </div>

      <div className="space-y-2 flex-1">
        {messages.length === 0 ? (
          <p className="text-black/40 text-xs text-center mt-8">
            No messages yet. Start a conversation!
          </p>
        ) : (
          messages.map((message, index) => (
            <div key={message.id} className="relative">
              {index > 0 && (
                <div className="absolute left-1/2 -top-1 transform -translate-x-1/2 text-[10px] text-black/30">
                  ↓
                </div>
              )}
              <CompactMessage message={message} />
            </div>
          ))
        )}
      </div>
    </div>
  );
}

