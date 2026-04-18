from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from services.model_router import route_to_client
from rag.rag_engine import build_retriever, augment_prompt_with_context
from utils.session_store import token_store
from uuid import uuid4
import inspect
import json

router = APIRouter()
active_streams: dict[str, bool] = {}


class AskRequest(BaseModel):
    username: str
    prompt: str
    model: str
    instruction: str
    use_rag: bool = False
    top_k: int = 3


class StopRequest(BaseModel):
    stream_id: str


def _is_streamable(obj) -> bool:
    return bool(obj) and (inspect.isgenerator(obj) or inspect.isasyncgen(obj))


def _encode_sse(payload: str, event: str | None = None) -> str:
    lines = payload.split("\n") if payload else [""]
    data_lines = "\n".join(f"data: {line}" for line in lines)
    event_line = f"event: {event}\n" if event else ""
    return f"{event_line}{data_lines}\n\n"


@router.post("/ask")
async def ask(payload: AskRequest, connection: Request, authorization: str = Header(None)):
    try:
        authorized = authorizationCheck(payload.username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{payload.username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{payload.username}'"})

        retriever = None

        if payload.use_rag:
            retriever = build_retriever(payload.username)
            print(f'using rag: {payload.use_rag}')
            updated_prompt, rag_used = augment_prompt_with_context(payload.prompt, retriever, top_k=payload.top_k)
        else:
            updated_prompt = payload.prompt
            rag_used = False

        res = route_to_client(updated_prompt, payload.username, payload.model, payload.instruction)
        res["rag_used"] = rag_used
        response_payload = res.get("response")

        if _is_streamable(response_payload):
            stream_id = str(uuid4())
            active_streams[stream_id] = True

            async def stream_wrapper():
                try:
                    yield _encode_sse(stream_id, event="stream_id")
                    metadata = json.dumps({
                        "provider": res.get("provider"),
                        "model_used": res.get("model_used"),
                        "rag_used": rag_used
                    })
                    yield _encode_sse(metadata, event="metadata")

                    for chunk in response_payload:
                        if not active_streams.get(stream_id):
                            yield _encode_sse("stream halted by stop", event="stopped")
                            return
                        if await connection.is_disconnected():
                            active_streams[stream_id] = False
                            return
                        text_chunk = chunk if chunk is not None else ""
                        if isinstance(text_chunk, dict):
                            text_chunk = json.dumps(text_chunk)
                        yield _encode_sse(str(text_chunk))

                    if active_streams.get(stream_id):
                        yield _encode_sse("stream completed", event="completion")
                except Exception as exc:
                    yield _encode_sse(json.dumps({"error": str(exc)}), event="error")
                finally:
                    active_streams.pop(stream_id, None)

            # return StreamingResponse(stream_wrapper(), media_type="text/event-stream")
            return StreamingResponse(
                stream_wrapper(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                    "Transfer-Encoding": "chunked"
                }
            )

        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/stop")
async def stop_stream(stop_request: StopRequest):
    stream_id = stop_request.stream_id
    print(f'stream_id: {stream_id}')
    if stream_id not in active_streams:
        return JSONResponse(status_code=404, content={"msg": "stream not active"})
    active_streams[stream_id] = False
    return JSONResponse(content={"stream_id": stream_id, "status": "stopping"})


def authorizationCheck(username, authorization):
    try:
        token = authorization.split("Bearer")[1].strip()
        return token_store.validToken(username, token)
    except Exception as e:
        print(str(e))
        return "err"
