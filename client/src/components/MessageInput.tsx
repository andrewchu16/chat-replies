"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { ArrowUp } from "lucide-react";

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
}

export default function MessageInput({
  onSendMessage,
  disabled = false,
}: MessageInputProps) {
  const [input, setInput] = useState("");
  const [rowCount, setRowCount] = useState(1);
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

      // Calculate approximate number of rows
      const lineHeight =
        parseInt(getComputedStyle(textareaRef.current).lineHeight) || 24;
      const paddingTop =
        parseInt(getComputedStyle(textareaRef.current).paddingTop) || 0;
      const paddingBottom =
        parseInt(getComputedStyle(textareaRef.current).paddingBottom) || 0;
      const contentHeight =
        textareaRef.current.scrollHeight - paddingTop - paddingBottom;
      const rows = Math.ceil(contentHeight / lineHeight);
      setRowCount(rows);
    }
  };

  useEffect(() => {
    autoResize();
  }, [input]);

  return (
    <form onSubmit={handleSend} className="w-full">
      <div className="relative rounded-2xl border border-black/10 bg-white focus-within:border-black/30 flex flex-col gap-2 px-2 py-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask, &quot;Give me a step-by-step guide to machine learning from scratch.&quot;"
          className={`max-h-32 pt-2 px-2 outline-none bg-transparent placeholder-black/30 resize-none ${
            rowCount >= 3 ? "overflow-auto custom-scrollbar" : "overflow-hidden"
          }`}
          rows={2}
          disabled={disabled}
        />
        <div className="flex justify-end">
          <button
            type="submit"
            className="h-8 w-8 rounded-full bg-black text-white text-sm disabled:opacity-40 flex items-center justify-center"
            disabled={!input.trim() || disabled}
            aria-label="Send"
          >
             <ArrowUp size={18} aria-hidden="true" />
          </button>
        </div>
      </div>
    </form>
  );
}
