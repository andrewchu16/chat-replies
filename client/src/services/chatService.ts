import { ChatMessage } from "../models/chat";
import { apiService, MessageReply } from "./api";

export class ChatService {
  private chatId: string | null = null;
  private messages: ChatMessage[] = [];

  async initializeChat(): Promise<void> {
    try {
      const chat = await apiService.createChat("New Chat");
      this.chatId = chat.id;
    } catch (error) {
      console.error("Failed to create chat:", error);
      throw error;
    }
  }

  async sendMessageStream(
    content: string,
    onUpdate: () => void,
    onComplete: () => void,
    onError: (error: string) => void
  ): Promise<void> {
    if (!this.chatId) {
      await this.initializeChat();
    }

    if (!this.chatId) {
      throw new Error("Failed to create chat");
    }

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: "user",
      content,
      timestamp: new Date(),
    };
    this.messages.push(userMessage);
    onUpdate(); // Notify UI of user message

    // Create AI message placeholder
    const aiMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: "ai",
      content: "",
      timestamp: new Date(),
    };
    this.messages.push(aiMessage);
    onUpdate(); // Notify UI of AI message placeholder

    try {
      await apiService.sendMessageStream(
        this.chatId,
        content,
        (chunk) => {
          // Add chunk content to AI message
          if (chunk.content) {
            aiMessage.content += chunk.content;
            onUpdate(); // Notify UI of content update
          }
        },
        (messageId) => {
          // Update AI message with final ID from server
          aiMessage.id = messageId;
          onComplete();
        },
        (error) => {
          // Remove the AI message on error
          const aiIndex = this.messages.findIndex(msg => msg.id === aiMessage.id);
          if (aiIndex !== -1) {
            this.messages.splice(aiIndex, 1);
          }
          onError(error);
        }
      );
    } catch (error) {
      console.error("Failed to send message:", error);
      // Remove the AI message on error
      const aiIndex = this.messages.findIndex(msg => msg.id === aiMessage.id);
      if (aiIndex !== -1) {
        this.messages.splice(aiIndex, 1);
      }
      onError(error instanceof Error ? error.message : "Unknown error");
    }
  }

  getMessages(): ChatMessage[] {
    return [...this.messages];
  }

  async loadMessages(): Promise<void> {
    if (!this.chatId) {
      return;
    }

    try {
      const apiMessages = await apiService.getChatMessages(this.chatId);
      this.messages = apiMessages.map((msg) => ({
        id: msg.id,
        sender: msg.sender as "user" | "assistant",
        content: msg.content,
        timestamp: new Date(msg.created_at),
      } as ChatMessage));
    } catch (error) {
      console.error("Failed to load messages:", error);
      throw error;
    }
  }

  async replyToMessage(
    messageId: string,
    content: string,
    replyMetadata?: { startIndex: number; endIndex: number }
  ): Promise<void> {
    if (!this.chatId) {
      throw new Error("No active chat");
    }

    const replyData: MessageReply = {
      content,
      sender: "user",
      reply_metadata: replyMetadata ? {
        start_index: replyMetadata.startIndex,
        end_index: replyMetadata.endIndex,
        parent_id: messageId,
      } : undefined,
    };

    try {
      const apiMessage = await apiService.replyToMessage(this.chatId, messageId, replyData);
      
      // Add the reply message to our local messages
      const replyMessage: ChatMessage = {
        id: apiMessage.id,
        sender: apiMessage.sender,
        content: apiMessage.content,
        timestamp: new Date(apiMessage.created_at),
      };
      this.messages.push(replyMessage);
    } catch (error) {
      console.error("Failed to reply to message:", error);
      throw error;
    }
  }

  async replyToMessageStream(
    messageId: string,
    content: string,
    replyMetadata: { startIndex: number; endIndex: number } | undefined,
    onUpdate: () => void,
    onComplete: () => void,
    onError: (error: string) => void
  ): Promise<void> {
    if (!this.chatId) {
      throw new Error("No active chat");
    }

    const replyData: MessageReply = {
      content,
      sender: "user",
      reply_metadata: replyMetadata ? {
        start_index: replyMetadata.startIndex,
        end_index: replyMetadata.endIndex,
        parent_id: messageId,
      } : undefined,
    };

    // Add user reply message immediately
    const userReplyMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: "user",
      content,
      timestamp: new Date(),
    };
    this.messages.push(userReplyMessage);
    onUpdate(); // Notify UI of user reply

    // Create AI response placeholder
    const aiMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: "ai",
      content: "",
      timestamp: new Date(),
    };
    this.messages.push(aiMessage);
    onUpdate(); // Notify UI of AI message placeholder

    try {
      await apiService.replyToMessageStream(
        this.chatId,
        messageId,
        replyData,
        (chunk) => {
          // Add chunk content to AI message
          if (chunk.content) {
            aiMessage.content += chunk.content + " ";
            onUpdate(); // Notify UI of content update
          }
        },
        (finalMessageId) => {
          // Update AI message with final ID from server
          aiMessage.id = finalMessageId;
          onComplete();
        },
        (error) => {
          // Remove the AI message on error
          const aiIndex = this.messages.findIndex(msg => msg.id === aiMessage.id);
          if (aiIndex !== -1) {
            this.messages.splice(aiIndex, 1);
          }
          onError(error);
        }
      );
    } catch (error) {
      console.error("Failed to reply to message:", error);
      // Remove the AI message on error
      const aiIndex = this.messages.findIndex(msg => msg.id === aiMessage.id);
      if (aiIndex !== -1) {
        this.messages.splice(aiIndex, 1);
      }
      onError(error instanceof Error ? error.message : "Unknown error");
    }
  }
}

export const chatService = new ChatService();
