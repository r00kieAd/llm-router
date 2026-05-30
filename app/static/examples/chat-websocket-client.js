export class ChatWebSocketClient {
  constructor({ baseUrl, username, token, onEvent }) {
    this.baseUrl = baseUrl.replace(/^http/, "ws").replace(/\/$/, "");
    this.username = username;
    this.token = token;
    this.onEvent = onEvent;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.heartbeatTimer = null;
    this.closedByClient = false;
    this.pendingStreams = new Map();
  }

  connect() {
    const url = new URL(`${this.baseUrl}/ws/chat`);
    url.searchParams.set("username", this.username);
    url.searchParams.set("token", this.token);

    this.socket = new WebSocket(url.toString());
    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.closedByClient = false;
      this.startHeartbeat();
    };
    this.socket.onmessage = (message) => this.handleMessage(message);
    this.socket.onclose = () => {
      this.stopHeartbeat();
      if (!this.closedByClient) {
        this.scheduleReconnect();
      }
    };
    this.socket.onerror = () => {
      this.socket?.close();
    };
  }

  disconnect() {
    this.closedByClient = true;
    this.stopHeartbeat();
    this.socket?.close(1000, "client closed");
  }

  ask({ prompt, model, instruction, useRag = false, topK = 3, useWeb = false }) {
    const requestId = crypto.randomUUID();
    this.send({
      type: "start_generation",
      request_id: requestId,
      payload: {
        prompt,
        model,
        instruction,
        use_rag: useRag,
        top_k: topK,
        use_web: useWeb,
      },
    });
    this.pendingStreams.set(requestId, { text: "" });
    return requestId;
  }

  cancel(streamId) {
    this.send({
      type: "cancel_generation",
      request_id: crypto.randomUUID(),
      payload: { stream_id: streamId },
    });
  }

  send(message) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("websocket is not connected");
    }
    this.socket.send(JSON.stringify(message));
  }

  handleMessage(message) {
    const event = JSON.parse(message.data);

    if (event.type === "ping") {
      this.send({ type: "pong", request_id: event.request_id });
      return;
    }

    if (event.type === "token") {
      const stream = this.pendingStreams.get(event.request_id) || { text: "" };
      stream.streamId = event.stream_id;
      stream.text += event.payload.text;
      this.pendingStreams.set(event.request_id, stream);
    }

    if (["completion", "cancelled", "error"].includes(event.type)) {
      this.pendingStreams.delete(event.request_id);
    }

    this.onEvent?.(event);
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.send({ type: "ping", request_id: crypto.randomUUID() });
      }
    }, 25000);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  scheduleReconnect() {
    const delay = Math.min(30000, 500 * 2 ** this.reconnectAttempts);
    this.reconnectAttempts += 1;
    setTimeout(() => this.connect(), delay);
  }
}

// Usage:
// const chat = new ChatWebSocketClient({
//   baseUrl: "https://api.example.com",
//   username,
//   token,
//   onEvent(event) {
//     if (event.type === "token") appendToken(event.payload.text);
//     if (event.type === "completion") markDone(event.stream_id);
//     if (event.type === "error") showError(event.payload.message);
//   },
// });
// chat.connect();
// const requestId = chat.ask({ prompt, model, instruction });
