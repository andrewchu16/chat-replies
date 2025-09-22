import { ChatMessageSender } from "./common";

export type ChatMessage = {
  id: string;
  sender: ChatMessageSender;
  content: string;
  timestamp?: Date;
};

export type ChatState = {
  messages: ChatMessage[];
  isLoading: boolean;
  error?: string;
};
