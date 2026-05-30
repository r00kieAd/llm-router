import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from services.generation_service import (
    ChatGenerationRequest,
    stream_generation,
    validate_bearer_token,
)

router = APIRouter()
active_streams: dict[str, asyncio.Event] = {}


class StopRequest(BaseModel):
    stream_id: str


def _encode_sse(payload: str, event: str | None = None) -> str:
    lines = payload.split("\n") if payload else [""]
    data_lines = "\n".join(f"data: {line}" for line in lines)
    event_line = f"event: {event}\n" if event else ""
    return f"{event_line}{data_lines}\n\n"


@router.post("/ask")
async def ask(payload: ChatGenerationRequest, connection: Request, authorization: str = Header(None)):
    try:
        authorized = validate_bearer_token(payload.username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{payload.username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{payload.username}'"})

        stream_id = str(uuid4())
        cancel_event = asyncio.Event()
        active_streams[stream_id] = cancel_event

        async def stream_wrapper():
            try:
                yield _encode_sse(stream_id, event="stream_id")
                async for event in stream_generation(payload, cancel_event=cancel_event):
                    if await connection.is_disconnected():
                        cancel_event.set()
                        return
                    event_type = event["type"]
                    event_payload = event["payload"]
                    if event_type == "token":
                        yield _encode_sse(event_payload["text"])
                    elif event_type == "completion":
                        yield _encode_sse("stream completed", event="completion")
                    elif event_type == "cancelled":
                        yield _encode_sse("stream halted by stop", event="stopped")
                    else:
                        yield _encode_sse(json.dumps(event_payload), event=event_type)
            finally:
                active_streams.pop(stream_id, None)

        return StreamingResponse(
            stream_wrapper(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Transfer-Encoding": "chunked",
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/stop")
async def stop_stream(stop_request: StopRequest):
    stream_id = stop_request.stream_id
    print(f'stream_id: {stream_id}')
    if stream_id not in active_streams:
        return JSONResponse(status_code=404, content={"msg": "stream not active"})
    active_streams[stream_id].set()
    return JSONResponse(content={"stream_id": stream_id, "status": "stopping"})
