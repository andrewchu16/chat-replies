# Server-Sent Events (SSE) Setup

This client is configured to receive AI messages as Server-Sent Events (SSE) from the backend server.

## Configuration

1. Copy the environment file:
   ```bash
   cp .env.local.example .env.local
   ```

2. Update the API URL in `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## How SSE Works

The client sends messages to the `/chats/{chat_id}/messages/stream` endpoint and receives streaming responses in the following format:

```
data: {"content": "Hello", "is_final": false, "message_id": null}

data: {"content": " there!", "is_final": false, "message_id": null}

data: {"content": " How can I help?", "is_final": true, "message_id": "uuid-here"}
```

## Features

- **Real-time streaming**: AI responses appear word-by-word as they're generated
- **Visual indicators**: 
  - Animated typing indicator while waiting for response
  - Blinking cursor at the end of streaming messages
  - Bouncing dots animation during loading
- **Error handling**: Graceful error display if streaming fails
- **Message persistence**: Messages are saved and loaded on page refresh

## API Integration

The client automatically:
1. Creates a new chat when first message is sent
2. Sends user messages to the backend
3. Receives streaming AI responses via SSE
4. Updates the UI in real-time as chunks arrive
5. Handles connection errors and retries

## Testing

To test the SSE functionality:

1. Start the backend server (FastAPI)
2. Start the client: `npm run dev`
3. Send a message and watch it stream in real-time
4. Check browser dev tools Network tab to see SSE connection
