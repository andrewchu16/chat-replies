"use client";

import ReactMarkdown from "react-markdown";
import { useEffect } from "react";
import { ChatMessage } from "../models/chat";
import ReplyButton from "./ReplyButton";

interface AIMessageProps {
  message: ChatMessage;
  isStreaming?: boolean;
  isLoading?: boolean;
  onReply?: (messageId: string, content: string, replyMetadata?: { startIndex: number; endIndex: number }) => void;
}

export default function AIMessage({ message, isStreaming = false, isLoading = false, onReply }: AIMessageProps) {
  useEffect(() => {
    // Log the raw message as received by the component for debugging markdown issues
    // Includes a short preview and full content
    console.log("[AIMessage] received", {
      id: message.id,
      sender: message.sender,
      isStreaming,
      isLoading,
      contentLength: message.content?.length ?? 0,
      contentPreview: message.content?.slice(0, 200),
      content: message.content,
    });
  }, [message.id, message.sender, message.content, isStreaming, isLoading]);

  return (
    <div className="w-full p-2">
      <div className="flex flex-col">
        <div className="text-sm leading-6 text-black/80 whitespace-normal break-words">
          <ReactMarkdown
            components={{
              p: ({ children }) => (<p className="mb-3">{children}</p>),
              ul: ({ children }) => (<ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>),
              ol: ({ children }) => (<ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>),
              li: ({ children }) => (<li>{children}</li>),
              strong: ({ children }) => (<strong className="font-semibold">{children}</strong>),
              em: ({ children }) => (<em className="italic">{children}</em>),
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noreferrer" className="underline text-blue-600 hover:text-blue-700">
                  {children}
                </a>
              ),
              pre: ({ children }) => (
                <pre className="bg-black/90 text-white rounded-lg p-3 overflow-x-auto text-[0.85em]">{children}</pre>
              ),
              code: ({ children }) => (
                <code className="px-1 py-0.5 bg-black/5 rounded font-mono text-[0.85em]">{children}</code>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
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
