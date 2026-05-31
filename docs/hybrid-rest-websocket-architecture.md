# Hybrid REST + WebSocket Architecture

This backend keeps ordinary request/response APIs on REST and moves only realtime generation traffic to WebSocket.

## Recommended Architecture

- REST remains authoritative for authentication, settings, chat history, uploads, model listing, file CRUD, and non-realtime operations.
- WebSocket is used only for token streaming, generation progress, cancel generation, tool-call events, and agent status updates.
- Shared generation code lives in `app/services/generation_service.py`. REST `/ask` and WebSocket `/ws/chat` both call this service, so RAG, web enrichment, memory, routing, and provider selection are not duplicated.
- WebSocket connection state lives in `app/ws/connection_manager.py`; active generation task state lives in `app/routes/websocket_chat.py`.
- In production, expose WebSocket only over `wss://` behind TLS.

## Backend Folder Structure

```text
app/
  main.py
  routes/
    prompt.py              # existing REST/SSE endpoint, now reuses generation_service
    websocket_chat.py      # /ws/chat realtime transport
  services/
    generation_service.py  # shared prompt prep, model routing, stream iteration, memory writes
    model_router.py        # existing provider/model routing
  ws/
    connection_manager.py  # per-user connection registry and serialized writes
```

## WebSocket Endpoint

```text
GET /ws/chat?username=<username>&token=<access-token>
```

Native browser WebSocket clients cannot reliably attach an `Authorization` header, so the endpoint accepts a short-lived token in the query string. For non-browser clients, a bearer header is also accepted.

## Event Envelope

Every message is JSON:

```json
{
  "type": "token",
  "event_id": "1e2f...",
  "stream_id": "9b23...",
  "request_id": "client-request-id",
  "ts": 1779542230123,
  "payload": {}
}
```

Client to server:

```json
{ "type": "start_generation", "request_id": "uuid", "payload": { "prompt": "...", "model": "gpt-5-mini", "instruction": "...", "use_rag": false, "top_k": 3, "use_web": false } }
{ "type": "cancel_generation", "request_id": "uuid", "payload": { "stream_id": "server-stream-id" } }
{ "type": "ping", "request_id": "uuid" }
{ "type": "pong", "request_id": "uuid" }
```

Server to client:

```json
{ "type": "connection_ack", "payload": { "heartbeat_interval_ms": 25000 } }
{ "type": "generation_started", "stream_id": "...", "payload": { "username": "..." } }
{ "type": "metadata", "stream_id": "...", "payload": { "provider": "OpenAI", "model_used": "gpt-5-mini", "rag_used": false, "web_used": false } }
{ "type": "token", "stream_id": "...", "payload": { "text": "Hello" } }
{ "type": "progress", "stream_id": "...", "payload": { "stage": "retrieving_context" } }
{ "type": "tool_call", "stream_id": "...", "payload": { "name": "web_search", "status": "started" } }
{ "type": "agent_status", "stream_id": "...", "payload": { "state": "thinking" } }
{ "type": "completion", "stream_id": "...", "payload": { "reason": "completed" } }
{ "type": "cancel_requested", "stream_id": "...", "payload": { "reason": "client_cancelled" } }
{ "type": "cancelled", "stream_id": "...", "payload": { "reason": "cancelled" } }
{ "type": "error", "stream_id": "...", "payload": { "message": "..." } }
```

`progress`, `tool_call`, and `agent_status` are reserved protocol events. The current service can emit them later without changing the connection contract.

## Frontend Migration

- Keep existing REST calls unchanged.
- Replace only the old streaming fetch/EventSource transport with a WebSocket transport.
- Open one WebSocket connection per authenticated browser session.
- Append `token.payload.text` to the current assistant message as events arrive.
- Mark the message complete on `completion`.
- Stop rendering and show status on `cancelled` or `error`.
- Reconnect with exponential backoff if the socket closes unexpectedly.
- Recreate interrupted generations explicitly from UI state if product requirements allow retry; do not blindly replay user prompts after reconnect.

Example client: `app/static/examples/chat-websocket-client.js`.

## Auth Strategy

- Continue to authenticate via REST.
- Return a normal API token or, preferably, a short-lived WebSocket token minted by REST.
- Connect with `wss://api.example.com/ws/chat?username=...&token=...`.
- Validate the token during the WebSocket handshake and close with code `1008` on failure.
- Keep token TTL short because query strings can appear in access logs.
- Use TLS only in production; never expose `ws://` over untrusted networks.

## Nginx / Reverse Proxy

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location /ws/ {
        proxy_pass http://app_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_buffering off;
    }

    location / {
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Scaling Considerations

- A single process can manage many idle WebSockets, but active LLM streams consume outbound sockets, provider quota, and memory.
- Enforce per-user and per-org concurrent generation limits.
- Use Redis or another shared store for distributed stream state if cancel requests may arrive at any worker.
- Prefer sticky sessions at the load balancer for WebSocket connections.
- For multi-worker fanout, publish server events through Redis pub/sub, NATS, or Kafka.
- Persist final chat messages through the same history service used by REST.
- Apply idle timeouts and heartbeat cleanup to remove dead corporate VPN/laptop connections.
- Emit metrics: connected sockets, active streams, token latency, cancellations, provider errors, reconnects.

## Production Best Practices

- Use WSS with modern TLS.
- Set explicit allowed origins; avoid wildcard CORS in production.
- Validate message size and schema.
- Rate limit `start_generation` and connection attempts.
- Use structured logs with `request_id`, `stream_id`, `username`, provider, and model.
- Treat WebSocket messages as untrusted input.
- Make cancellation idempotent.
- Do not put long-lived secrets in query strings; use short-lived scoped WebSocket tokens.
- Keep REST as the source of truth for settings, history, uploads, and CRUD.

## Enterprise Network Behavior

SSE and chunked HTTP streaming often fail on enterprise laptops because proxies, VPN agents, DLP scanners, antivirus TLS inspection, and secure web gateways may buffer HTTP response bodies until a minimum size or until the response completes. Some devices also strip or ignore `X-Accel-Buffering: no`, compress streams, enforce idle HTTP response timeouts, or downgrade behavior across HTTP/2 to HTTP/1.1 boundaries.

WebSockets are often more reliable because the connection upgrades once and then uses message frames over a long-lived TCP/TLS session. Enterprise proxies that allow WebSockets generally tunnel frames without applying normal HTTP response buffering rules. WebSockets also provide bidirectional control, so cancel, heartbeat, progress, and token events share one realtime channel.

## Tradeoffs

REST:
- Best for simple request/response APIs, caching, auth, CRUD, uploads, settings, and history.
- Poor fit for token-by-token realtime responses.

SSE/chunked HTTP:
- Simple one-way server-to-client streaming.
- Works well on clean networks.
- Vulnerable to buffering by enterprise proxies and harder to use for client-to-server controls like cancel.

WebSocket:
- Best for bidirectional realtime LLM sessions.
- Supports token streaming, cancel, heartbeat, progress, tool events, and status updates.
- Requires explicit connection lifecycle, auth, load-balancer support, observability, and cleanup.
