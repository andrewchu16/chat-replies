import { ApiChat, ApiMessage, StreamChunk, MessageReply } from "../models/api";

export type { ApiChat, ApiMessage, StreamChunk, MessageReply };

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async createChat(title?: string): Promise<ApiChat> {
    const response = await fetch(`${this.baseUrl}/chats/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create chat: ${response.statusText}`);
    }

    return response.json();
  }

  async sendMessage(chatId: string, content: string): Promise<ApiMessage> {
    // Fallback non-stream helper built on top of streaming endpoint
    const messageId = await new Promise<string>((resolve, reject) => {
      this.sendMessageStream(
        chatId,
        content,
        () => {},
        (finalMessageId) => resolve(finalMessageId),
        (error) => reject(new Error(error))
      ).catch(reject);
    });

    const finalResponse = await fetch(
      `${this.baseUrl}/chats/${chatId}/messages/${messageId}`
    );
    if (!finalResponse.ok) {
      throw new Error(`Failed to fetch created message: ${finalResponse.statusText}`);
    }
    return finalResponse.json();
  }

  async sendMessageStream(
    chatId: string,
    content: string,
    onChunk: (chunk: StreamChunk) => void,
    onComplete: (messageId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/chats/${chatId}/messages/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          "Cache-Control": "no-cache",
        },
        body: JSON.stringify({
          content,
          sender: "user",
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("No response body");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              // Handle error responses from server
              if (data.error) {
                onError(data.error);
                return;
              }

              // Handle streaming chunks
              if (data.content !== undefined) {
                onChunk(data);
              }

              // Handle final message
              if (data.is_final && data.message_id) {
                onComplete(data.message_id);
              }
            } catch (error) {
              console.error("Error parsing SSE data:", error);
              onError("Failed to parse response");
            }
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : "Unknown error");
    } finally {
      reader.releaseLock();
    }
  }

  async getChatMessages(
    chatId: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<ApiMessage[]> {
    const response = await fetch(
      `${this.baseUrl}/chats/${chatId}/messages?skip=${skip}&limit=${limit}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get messages: ${response.statusText}`);
    }

    const data = await response.json();
    return data.messages;
  }

  async replyToMessage(
    chatId: string,
    messageId: string,
    replyData: MessageReply
  ): Promise<ApiMessage> {
    // Fallback non-stream helper built on top of streaming endpoint
    const aiMessageId = await new Promise<string>((resolve, reject) => {
      this.replyToMessageStream(
        chatId,
        messageId,
        replyData,
        () => {},
        (finalMessageId) => resolve(finalMessageId),
        (error) => reject(new Error(error))
      ).catch(reject);
    });

    const finalResponse = await fetch(
      `${this.baseUrl}/chats/${chatId}/messages/${aiMessageId}`
    );
    if (!finalResponse.ok) {
      throw new Error(`Failed to fetch created reply: ${finalResponse.statusText}`);
    }
    return finalResponse.json();
  }

  async replyToMessageStream(
    chatId: string,
    messageId: string,
    replyData: MessageReply,
    onChunk: (chunk: StreamChunk) => void,
    onComplete: (messageId: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/chats/${chatId}/messages/${messageId}/reply/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          "Cache-Control": "no-cache",
        },
        body: JSON.stringify(replyData),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to reply to message: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("No response body");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              // Handle error responses from server
              if (data.error) {
                onError(data.error);
                return;
              }

              // Handle streaming chunks
              if (data.content !== undefined) {
                onChunk(data);
              }

              // Handle final message
              if (data.is_final && data.message_id) {
                onComplete(data.message_id);
              }
            } catch (error) {
              console.error("Error parsing SSE data:", error);
              onError("Failed to parse response");
            }
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : "Unknown error");
    } finally {
      reader.releaseLock();
    }
  }
}

export const apiService = new ApiService();
