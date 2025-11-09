"use client";

import { useState, useEffect } from "react";
import { ChatMessage } from "../models/chat";
import { apiService } from "../services/api";

interface ReplyChainProps {
  chatId: string | null;
  messageId: string | null;
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

export default function ReplyChain({ chatId, messageId }: ReplyChainProps) {
  const [replyChain, setReplyChain] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadReplyChain = async () => {
      if (!chatId || !messageId) {
        setReplyChain([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const apiMessages = await apiService.getReplyChain(chatId, messageId);
        const messages: ChatMessage[] = apiMessages.map((msg) => ({
          id: msg.id,
          sender: msg.sender,
          content: msg.content,
          timestamp: new Date(msg.created_at),
        }));
        setReplyChain(messages);
      } catch (err) {
        console.error("Failed to load reply chain:", err);
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load reply chain";

        // If message not found, show a user-friendly message
        if (errorMessage.includes("not found")) {
          setError(
            "This message hasn't been saved yet. Try selecting it again after the response completes."
          );
        } else {
          setError(errorMessage);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadReplyChain();
  }, [chatId, messageId]);

  if (!chatId || !messageId) {
    return (
      <div className="w-full h-full border border-black/10 rounded-2xl p-4 flex items-center justify-center">
        <p className="text-black/40 text-sm text-center">
          Select a message to view its reply chain
        </p>
      </div>
    );
  }

  return (
    <div className="w-full h-full border border-black/10 rounded-2xl p-4 overflow-y-auto flex flex-col min-h-0">
      <div className="mb-3 pb-2 border-b border-black/10">
        <h2 className="text-base font-semibold text-black">Context Preview</h2>
        <p className="text-[11px] text-black/50 mt-0.5">
          Messages sent to AI ({replyChain.length} message
          {replyChain.length !== 1 ? "s" : ""})
        </p>
      </div>

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-sm text-black/40 italic flex items-center gap-2">
            <div className="flex gap-1">
              <div
                className="w-1 h-1 bg-black/40 rounded-full animate-bounce"
                style={{ animationDelay: "0ms" }}
              ></div>
              <div
                className="w-1 h-1 bg-black/40 rounded-full animate-bounce"
                style={{ animationDelay: "150ms" }}
              ></div>
              <div
                className="w-1 h-1 bg-black/40 rounded-full animate-bounce"
                style={{ animationDelay: "300ms" }}
              ></div>
            </div>
            Loading...
          </div>
        </div>
      ) : error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-xs text-red-600 text-center">{error}</div>
        </div>
      ) : (
        <div className="space-y-2 flex-1">
          {replyChain.length === 0 ? (
            <p className="text-black/40 text-xs text-center mt-8">
              No messages in context.
            </p>
          ) : (
            replyChain.map((message, index) => (
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
      )}
    </div>
  );
}
