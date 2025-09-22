import { ChatMessageSender } from "./common";

export interface ApiMessage {
  id: string;
  chat_id: string;
  content: string;
  sender: ChatMessageSender;
  created_at: string;
  reply_metadata: any[];
}

export interface ApiChat {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface StreamChunk {
  content: string;
  is_final: boolean;
  message_id?: string;
}

export interface MessageReplyMetadata {
  start_index: number;
  end_index: number;
}

export interface MessageReply {
  content: string;
  sender: ChatMessageSender;
  reply_metadata?: MessageReplyMetadata;
}
