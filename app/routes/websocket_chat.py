import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from services.generation_service import ChatGenerationRequest, stream_generation, validate_token
from ws.connection_manager import manager

router = APIRouter()

HEARTBEAT_INTERVAL_SECONDS = 25
HEARTBEAT_TIMEOUT_SECONDS = 75


@dataclass
class ActiveGeneration:
    username: str
    websocket: WebSocket
    request_id: str | None
    cancel_event: asyncio.Event
    task: asyncio.Task | None = None


active_generations: dict[str, ActiveGeneration] = {}


@router.get("/ws/chat")
@router.get("/ws/ask")
async def websocket_http_diagnostic(request: Request):
    websocket_headers = {
        "connection": request.headers.get("connection"),
        "upgrade": request.headers.get("upgrade"),
        "sec_websocket_version": request.headers.get("sec-websocket-version"),
        "sec_websocket_key_present": bool(request.headers.get("sec-websocket-key")),
        "origin": request.headers.get("origin"),
        "user_agent": request.headers.get("user-agent"),
    }
    print(f"[websocket] HTTP request reached websocket endpoint without upgrade headers: {websocket_headers}")
    return JSONResponse(
        status_code=426,
        content={
            "error": "websocket_upgrade_required",
            "detail": "This endpoint only works with a WebSocket upgrade request. If a browser WebSocket logs as HTTP GET here, a proxy or server is not forwarding the Upgrade headers.",
            "received_headers": websocket_headers,
        },
        headers={"Upgrade": "websocket", "Connection": "Upgrade"},
    )


def envelope(
    event_type: str,
    *,
    stream_id: str | None = None,
    request_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "type": event_type,
        "event_id": str(uuid4()),
        "stream_id": stream_id,
        "request_id": request_id,
        "ts": int(time.time() * 1000),
        "payload": payload or {},
    }


def frontend_event(
    event_type: str,
    *,
    stream_id: str | None = None,
    request_id: str | None = None,
    sequence: int | None = None,
    **payload: Any,
) -> dict[str, Any]:
    event = {
        "type": event_type,
        "event_id": str(uuid4()),
        "request_id": request_id,
        "session_id": stream_id,
        "stream_id": stream_id,
        "ts": int(time.time() * 1000),
        **payload,
    }
    if sequence is not None:
        event["sequence"] = sequence
    return event


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


async def _run_generation(
    websocket: WebSocket,
    request: ChatGenerationRequest,
    stream_id: str,
    request_id: str | None,
    cancel_event: asyncio.Event,
) -> None:
    full_response: list[str] = []
    stream_metadata: dict[str, Any] = {}
    sequence = 0
    try:
        await manager.send(
            websocket,
            frontend_event(
                "stream_start",
                stream_id=stream_id,
                request_id=request_id,
                username=request.username,
            ),
        )
        async for event in stream_generation(request, cancel_event=cancel_event):
            event_type = event["type"]
            payload = event["payload"]
            if event_type == "metadata":
                stream_metadata = payload
                await manager.send(
                    websocket,
                    frontend_event("metadata", stream_id=stream_id, request_id=request_id, **payload),
                )
            elif event_type == "token":
                sequence += 1
                token = payload.get("text", "")
                full_response.append(token)
                await manager.send(
                    websocket,
                    frontend_event(
                        "token",
                        stream_id=stream_id,
                        request_id=request_id,
                        sequence=sequence,
                        token=token,
                    ),
                )
            elif event_type == "completion":
                await manager.send(
                    websocket,
                    frontend_event(
                        "stream_end",
                        stream_id=stream_id,
                        request_id=request_id,
                        response="".join(full_response),
                        **stream_metadata,
                    ),
                )
            elif event_type == "cancelled":
                await manager.send(
                    websocket,
                    frontend_event(
                        "cancelled",
                        stream_id=stream_id,
                        request_id=request_id,
                        reason=payload.get("reason", "cancelled"),
                    ),
                )
            elif event_type == "error":
                await manager.send(
                    websocket,
                    frontend_event(
                        "error",
                        stream_id=stream_id,
                        request_id=request_id,
                        message=payload.get("message", "generation failed"),
                        code="GENERATION_ERROR",
                        retryable=False,
                    ),
                )
            else:
                await manager.send(
                    websocket,
                    frontend_event(event_type, stream_id=stream_id, request_id=request_id, **payload),
                )
            if event_type in {"completion", "cancelled", "error"}:
                break
    except asyncio.CancelledError:
        cancel_event.set()
        await manager.send(
            websocket,
            frontend_event(
                "cancelled",
                stream_id=stream_id,
                request_id=request_id,
                reason="connection_closed",
            ),
        )
        raise
    except Exception as exc:
        await manager.send(
            websocket,
            frontend_event(
                "error",
                stream_id=stream_id,
                request_id=request_id,
                message=str(exc),
                code="SERVER_ERROR",
                retryable=False,
            ),
        )
    finally:
        active_generations.pop(stream_id, None)


async def _cancel_stream(stream_id: str, reason: str = "client_cancelled") -> bool:
    active = active_generations.get(stream_id)
    if not active:
        return False
    active.cancel_event.set()
    await manager.send(
        active.websocket,
        frontend_event("cancelled", stream_id=stream_id, request_id=active.request_id, reason=reason),
    )
    return True


async def _cancel_socket_generations(websocket: WebSocket) -> None:
    stream_ids = [stream_id for stream_id, active in active_generations.items() if active.websocket == websocket]
    for stream_id in stream_ids:
        active = active_generations.get(stream_id)
        if active:
            active.cancel_event.set()
            if active.task:
                active.task.cancel()
    await asyncio.gather(
        *(
            active_generations[stream_id].task
            for stream_id in stream_ids
            if stream_id in active_generations and active_generations[stream_id].task
        ),
        return_exceptions=True,
    )


@router.websocket("/ws/ask")
@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    username: str | None = Query(None),
    token: str | None = Query(None),
    authorization: str | None = Header(None),
):
    if not username:
        print("[websocket] rejected connection: missing username query parameter")
        await websocket.close(code=1008)
        return

    auth_token = token or _bearer_token(authorization)
    if not validate_token(username, auth_token):
        print(f"[websocket] rejected connection: invalid token for user='{username}'")
        await websocket.close(code=1008)
        return

    await manager.connect(username, websocket)
    print(f"[websocket] connected user='{username}'")
    await manager.send(
        websocket,
        envelope(
            "connection_ack",
            payload={
                "username": username,
                "heartbeat_interval_ms": HEARTBEAT_INTERVAL_SECONDS * 1000,
            },
        ),
    )

    close_reason = "unknown"
    try:
        while True:
            state = manager.state(websocket)
            if state and time.time() - state.last_seen > HEARTBEAT_TIMEOUT_SECONDS:
                await websocket.close(code=1001)
                break

            try:
                message = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=HEARTBEAT_INTERVAL_SECONDS,
                )
            except asyncio.TimeoutError:
                await manager.send(websocket, envelope("ping"))
                continue
            except json.JSONDecodeError as exc:
                close_reason = "invalid_json"
                print(f"[websocket] invalid JSON from user='{username}': {exc}")
                await manager.send(
                    websocket,
                    envelope("error", payload={"message": "websocket message must be valid JSON"}),
                )
                continue

            manager.touch(websocket)
            message_type = message.get("type")
            request_id = message.get("request_id")
            payload = message.get("payload") or {}

            if message_type == "pong":
                continue

            if message_type == "ping":
                await manager.send(
                    websocket,
                    frontend_event(
                        "pong",
                        request_id=request_id,
                        sent_at=message.get("sent_at"),
                    ),
                )
                continue

            if message_type in {"cancel_generation", "cancel"}:
                stream_id = (
                    payload.get("stream_id")
                    or payload.get("session_id")
                    or message.get("stream_id")
                    or message.get("session_id")
                )
                cancelled = await _cancel_stream(stream_id) if stream_id else False
                if not cancelled:
                    await manager.send(
                        websocket,
                        frontend_event(
                            "error",
                            stream_id=stream_id,
                            request_id=request_id,
                            message="stream not active",
                            code="STREAM_NOT_ACTIVE",
                            retryable=False,
                        ),
                    )
                continue

            if message_type == "resume":
                print(
                    "[websocket] resume requested but replay is not available; "
                    f"user='{username}' request_id='{request_id}' session_id='{message.get('session_id')}'"
                )
                continue

            if message_type != "start_generation":
                await manager.send(
                    websocket,
                    frontend_event(
                        "error",
                        request_id=request_id,
                        message=f"unsupported message type: {message_type}",
                        code="UNSUPPORTED_MESSAGE_TYPE",
                        retryable=False,
                    ),
                )
                continue

            stream_id = str(uuid4())
            payload.pop("username", None)
            try:
                generation_request = ChatGenerationRequest(username=username, **payload)
            except Exception as exc:
                await manager.send(
                    websocket,
                    frontend_event(
                        "error",
                        stream_id=stream_id,
                        request_id=request_id,
                        message=str(exc),
                        code="INVALID_GENERATION_REQUEST",
                        retryable=False,
                    ),
                )
                continue
            cancel_event = asyncio.Event()
            active_generations[stream_id] = ActiveGeneration(
                username=username,
                websocket=websocket,
                request_id=request_id,
                cancel_event=cancel_event,
            )
            task = asyncio.create_task(
                _run_generation(
                    websocket,
                    generation_request,
                    stream_id,
                    request_id,
                    cancel_event,
                )
            )
            active_generations[stream_id].task = task
    except WebSocketDisconnect as exc:
        close_reason = f"client_disconnected code={exc.code}"
    except Exception as exc:
        close_reason = f"server_error {type(exc).__name__}: {exc}"
        print(f"[websocket] server error for user='{username}': {type(exc).__name__}: {exc}")
    finally:
        await _cancel_socket_generations(websocket)
        await manager.disconnect(websocket)
        print(f"[websocket] disconnected user='{username}' reason='{close_reason}'")
