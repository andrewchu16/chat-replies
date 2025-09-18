"use client";

import { useState, FormEvent } from "react";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");

  const handleSend = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
  };

  return (
    <div className="min-h-screen bg-white text-black">
      <main className="mx-auto max-w-xl px-4 sm:px-6 md:px-8 py-12">
        <div className="flex flex-col items-center">
          <h1 className="text-xl font-medium tracking-tight mb-8">Chat</h1>

          <div className="w-full border border-black/10 rounded-2xl p-4 mb-4">
            <div className="min-h-[40vh] max-h-[60vh] overflow-y-auto space-y-3">
              {messages.length === 0 ? (
                <p className="text-black/40 text-sm text-center mt-8">
                  Your conversation will appear here.
                </p>
              ) : (
                messages.map((m) => (
                  <div
                    key={m.id}
                    className={
                      m.role === "user"
                        ? "text-sm"
                        : "text-sm text-black/70"
                    }
                  >
                    {m.content}
                  </div>
                ))
              )}
            </div>
          </div>

          <form onSubmit={handleSend} className="w-full">
            <div className="flex items-center gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type a message"
                className="w-full h-12 px-4 rounded-full border border-black/10 outline-none focus:border-black/30 bg-white placeholder-black/30"
              />
              <button
                type="submit"
                className="h-12 px-5 rounded-full bg-black text-white text-sm disabled:opacity-40"
                disabled={!input.trim()}
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
