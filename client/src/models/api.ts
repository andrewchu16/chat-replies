import { ChatMessageSender } from "./common";

export interface MessageReplyMetadataResponse {
  id: string;
  message_id: string;
  start_index: number;
  end_index: number;
  created_at: string;
}

export interface ApiMessage {
  id: string;
  chat_id: string;
  content: string;
  sender: ChatMessageSender;
  created_at: string;
  reply_metadata: MessageReplyMetadataResponse | null;
}

export interface ApiChat {
  id: string;
  title: string;
  created_at: string;
  updated_at: string | null;
}

export interface StreamChunk {
  content: string;
  is_final: boolean;
  message_id?: string;
}

export interface MessageReplyMetadata {
  start_index: number;
  end_index: number;
  parent_id: string;
}

export interface MessageReply {
  content: string;
  sender: ChatMessageSender;
  reply_metadata?: MessageReplyMetadata;
}
