"use client";

import { ChatMessage } from "../models/chat";

interface UserMessageProps {
  message: ChatMessage;
}

export default function UserMessage({ message }: UserMessageProps) {
  return (
    <div className="w-full bg-gray-100 rounded-xl px-4 py-3">
      <div className="text-sm whitespace-pre-wrap">
        {message.content}
      </div>
    </div>
  );
}
