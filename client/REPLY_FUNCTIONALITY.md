# Reply Functionality

This document describes the reply functionality implemented in the chat client.

## Overview

The client now supports replying to AI messages with both regular and streaming responses. Users can reply to specific messages and optionally reference specific text within those messages.

## Features

### 1. Reply Button
- Each AI message displays a "Reply" button
- Clicking the button opens a reply interface
- Users can type their reply and optionally select specific text to reference

### 2. Text Selection
- Users can select text from the original message to reference in their reply
- The selected text is highlighted and included in the reply metadata
- This allows for context-aware responses from the AI

### 3. Streaming Replies
- Replies support both regular and streaming responses
- Streaming replies show real-time AI responses as they're generated
- Visual indicators show when a reply is being streamed

## API Endpoints

### Regular Reply
```
POST /chats/{chat_id}/messages/{message_id}/reply
```

### Streaming Reply
```
POST /chats/{chat_id}/messages/{message_id}/reply/stream
```

## Data Structures

### MessageReply
```typescript
interface MessageReply {
  content: string;
  sender: "user" | "ai";
  reply_metadata?: MessageReplyMetadata;
}
```

### MessageReplyMetadata
```typescript
interface MessageReplyMetadata {
  start_index: number;
  end_index: number;
}
```

## Usage Examples

### Basic Reply
```typescript
await chatService.replyToMessage(
  messageId,
  "Can you explain this further?",
  undefined // No specific text reference
);
```

### Reply with Text Reference
```typescript
await chatService.replyToMessage(
  messageId,
  "What does this mean?",
  { startIndex: 10, endIndex: 25 } // Reference specific text
);
```

### Streaming Reply
```typescript
await chatService.replyToMessageStream(
  messageId,
  "Please elaborate on this point",
  { startIndex: 0, endIndex: 15 },
  () => { /* Update UI */ },
  () => { /* Complete */ },
  (error) => { /* Handle error */ }
);
```

## UI Components

### ReplyButton
- Displays reply interface when clicked
- Handles text selection and reply composition
- Integrates with the chat service for sending replies

### MessageList
- Shows reply buttons on AI messages
- Handles reply callbacks and updates
- Displays streaming indicators for replies

## Error Handling

- Network errors are displayed to the user
- Failed replies are cleaned up from the UI
- Streaming errors remove incomplete messages

## Future Enhancements

- Thread view for replies
- Reply notifications
- Reply history and navigation
- Rich text formatting in replies
