"use client";

import ReactMarkdown from "react-markdown";
import { ChatMessage } from "../models/chat";
import ReplyButton from "./ReplyButton";

interface AIMessageProps {
  message: ChatMessage;
  isStreaming?: boolean;
  isLoading?: boolean;
  onReply?: (messageId: string, content: string, replyMetadata?: { startIndex: number; endIndex: number }) => void;
}

export default function AIMessage({ message, isStreaming = false, isLoading = false, onReply }: AIMessageProps) {
  return (
    <div className="w-full p-2">
      <div className="flex flex-col">
        <div className="text-sm text-black/70 prose prose-sm max-w-none">
          <ReactMarkdown>{message.content}</ReactMarkdown>
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-black/70 ml-1 streaming-cursor"></span>
          )}
        </div>
        
        {onReply && (
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
  );
}
