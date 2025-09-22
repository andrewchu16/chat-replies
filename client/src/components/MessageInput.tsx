"use client";

import { useState, useRef, useEffect, FormEvent } from "react";

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
}

export default function MessageInput({ onSendMessage, disabled = false }: MessageInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    onSendMessage(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const trimmed = input.trim();
      if (trimmed) {
        onSendMessage(trimmed);
        setInput("");
      }
    }
  };

  const autoResize = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  useEffect(() => {
    autoResize();
  }, [input]);

  return (
    <form onSubmit={handleSend} className="w-full">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message (Shift+Enter for new line)"
          className="w-full min-h-[48px] max-h-32 px-4 py-3 rounded-2xl border border-black/10 outline-none focus:border-black/30 bg-white placeholder-black/30 resize-none"
          rows={1}
          disabled={disabled}
        />
        <button
          type="submit"
          className="h-12 px-5 rounded-full bg-black text-white text-sm disabled:opacity-40 flex-shrink-0"
          disabled={!input.trim() || disabled}
        >
          Send
        </button>
      </div>
    </form>
  );
}
