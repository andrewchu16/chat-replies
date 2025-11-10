"use client";

import { useState, useEffect } from "react";
import { ChatMessage } from "../models/chat";
import { chatService } from "../services/chatService";
import MessageList from "./MessageList";
import MessageInput, { ReplyState } from "./MessageInput";
import ReplyChain from "./ReplyChain";
import ConversationHistory from "./ConversationHistory";

export default function ChatContainer() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(
    null
  );
  const [replyState, setReplyState] = useState<ReplyState | null>(null);
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [chatId, setChatId] = useState<string | null>(null);

  const handleSend = async (content: string) => {
    setIsLoading(true);
    setError(null);
    setStreamingMessageId(null);

    try {
      // Ensure chatId is set
      const currentChatId = chatService.getChatId();
      if (!currentChatId) {
        await chatService.initializeChat();
        setChatId(chatService.getChatId());
      }

      await chatService.sendMessageStream(
        content,
        () => {
          // Update messages with streaming content
          const currentMessages = chatService.getMessages();
          setMessages(currentMessages);

          // Find the AI message that's being streamed
          const aiMessage = currentMessages.find(
            (msg) =>
              msg.sender === "ai" &&
              msg.content &&
              !msg.content.trim().endsWith(".")
          );
          if (aiMessage && !streamingMessageId) {
            setStreamingMessageId(aiMessage.id);
          }
        },
        () => {
          setIsLoading(false);
          setStreamingMessageId(null);
        },
        (error) => {
          setError(error);
          setIsLoading(false);
          setStreamingMessageId(null);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      setIsLoading(false);
      setStreamingMessageId(null);
    }
  };

  const handleReply = async (
    messageId: string,
    content: string,
    replyMetadata?: { startIndex: number; endIndex: number }
  ) => {
    setIsLoading(true);
    setError(null);
    setStreamingMessageId(null);
    setReplyState(null); // Clear reply state after sending
    setSelectedMessageId(null); // Clear selected message to show conversation history

    try {
      await chatService.replyToMessageStream(
        messageId,
        content,
        replyMetadata,
        () => {
          // Update messages with streaming content
          const currentMessages = chatService.getMessages();
          setMessages(currentMessages);

          // Find the AI message that's being streamed
          const aiMessage = currentMessages.find(
            (msg) =>
              msg.sender === "ai" &&
              msg.content &&
              !msg.content.trim().endsWith(".")
          );
          if (aiMessage && !streamingMessageId) {
            setStreamingMessageId(aiMessage.id);
          }
        },
        () => {
          setIsLoading(false);
          setStreamingMessageId(null);
        },
        (error) => {
          setError(error);
          setIsLoading(false);
          setStreamingMessageId(null);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send reply");
      setIsLoading(false);
      setStreamingMessageId(null);
    }
  };

  const handleStartReply = (
    messageId: string,
    messageContent: string,
    replyMetadata?: { startIndex: number; endIndex: number }
  ) => {
    setReplyState({
      messageId,
      messageContent,
      replyMetadata,
    });
    // Show the context chain when replying
    setSelectedMessageId(messageId);
  };

  const handleCancelReply = () => {
    setReplyState(null);
    setSelectedMessageId(null); // Clear selected message to show conversation history
  };

  // Load existing messages on component mount
  useEffect(() => {
    const loadMessages = async () => {
      try {
        await chatService.loadMessages();
        setMessages(chatService.getMessages());
        setChatId(chatService.getChatId());
      } catch (err) {
        console.error("Failed to load messages:", err);
        // Don't show error for initial load failure
      }
    };

    loadMessages();
  }, []);

  // Update chatId when it becomes available
  useEffect(() => {
    const currentChatId = chatService.getChatId();
    if (currentChatId && currentChatId !== chatId) {
      setChatId(currentChatId);
    }
  }, [chatId]);


  // Determine if we should show the reply chain
  // Don't show reply chain for user messages
  const selectedMessage = messages.find((msg) => msg.id === selectedMessageId);
  const shouldShowReplyChain = selectedMessage?.sender !== "user";
  const replyChainMessageId = shouldShowReplyChain ? selectedMessageId : null;

  return (
    <div className="flex flex-row gap-4 w-full h-full min-h-0">
      {/* Left side: Chat window */}
      <div className="flex flex-col items-center w-1/2 h-full min-h-0">
        {error && (
          <div className="w-full mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}
        <MessageList
          messages={messages}
          isLoading={isLoading}
          streamingMessageId={streamingMessageId || undefined}
          onReply={handleStartReply}
        />
        <MessageInput
          onSendMessage={handleSend}
          onReply={handleReply}
          disabled={isLoading}
          replyState={replyState}
          onCancelReply={handleCancelReply}
        />
      </div>

      {/* Right side: Reply chain or conversation history */}
      <div className="w-1/2 h-full min-h-0">
        {replyChainMessageId ? (
          <ReplyChain chatId={chatId} messageId={replyChainMessageId} />
        ) : (
          <ConversationHistory messages={messages} />
        )}
      </div>
    </div>
  );
}
