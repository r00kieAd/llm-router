import asyncio
import inspect
import json
from dataclasses import dataclass
from typing import Any, AsyncIterator

from pydantic import BaseModel

from rag.rag_engine import augment_prompt_with_context, build_retriever
from services.model_router import route_to_client
from services.web_search_agent import enrich_prompt_with_web
from services.manage_memory import mem_instance
from utils.session_store import token_store


class ChatGenerationRequest(BaseModel):
    username: str
    prompt: str
    model: str
    instruction: str
    use_rag: bool = False
    top_k: int = 3
    use_web: bool = False
    is_local: bool = False


@dataclass
class PreparedGeneration:
    response: Any
    metadata: dict[str, Any]
    raw_result: dict[str, Any]
    full_response: list[str]
    persist_response: bool = True


class GenerationCancelled(Exception):
    pass


def validate_bearer_token(username: str, authorization: str | None) -> bool | str:
    try:
        if not authorization:
            return False
        token = authorization.split("Bearer")[1].strip()
        return token_store.validToken(username, token)
    except Exception as exc:
        print(str(exc))
        return "err"


def validate_token(username: str, token: str | None) -> bool:
    if not token:
        return False
    return token_store.validToken(username, token)


def is_streamable(obj: Any) -> bool:
    return bool(obj) and (inspect.isgenerator(obj) or inspect.isasyncgen(obj))


def normalize_chunk(chunk: Any) -> str:
    if chunk is None:
        return ""
    if isinstance(chunk, dict):
        return json.dumps(chunk)
    return str(chunk)


def prepare_generation(payload: ChatGenerationRequest) -> PreparedGeneration:
    mem = mem_instance
    mem_updated, context = mem.add_new_prompt(prompt=payload.prompt, username=payload.username)

    if payload.use_rag:
        retriever = build_retriever(payload.username)
        updated_prompt, rag_used = augment_prompt_with_context(
            payload.prompt,
            retriever,
            top_k=payload.top_k,
        )
        updated_prompt = f"{updated_prompt}\n{context}" if mem_updated else updated_prompt
    else:
        updated_prompt = payload.prompt if not mem_updated else context
        rag_used = False

    web_metadata = {"web_used": False}
    if payload.use_web:
        updated_prompt, web_metadata = enrich_prompt_with_web(
            updated_prompt,
            raw_prompt=payload.prompt,
        )

    if payload.is_local:
        result = {
            "response": updated_prompt,
            "provider": "local",
            "model_used": payload.model,
            "rag_used": rag_used,
            **web_metadata,
        }
        metadata = {
            "provider": result.get("provider"),
            "model_used": result.get("model_used"),
            "rag_used": rag_used,
            "web_used": web_metadata.get("web_used", False),
            "web_query": web_metadata.get("web_query"),
            "web_tool": web_metadata.get("web_tool"),
            "web_sources": web_metadata.get("web_sources", []),
            "local_prompt": updated_prompt,
        }
        return PreparedGeneration(
            response=result.get("response"),
            metadata=metadata,
            raw_result=result,
            full_response=[],
            persist_response=False,
        )

    result = route_to_client(updated_prompt, payload.username, payload.model, payload.instruction)
    result["rag_used"] = rag_used
    result.update(web_metadata)

    metadata = {
        "provider": result.get("provider"),
        "model_used": result.get("model_used"),
        "rag_used": rag_used,
        "web_used": web_metadata.get("web_used", False),
        "web_query": web_metadata.get("web_query"),
        "web_tool": web_metadata.get("web_tool"),
        "web_sources": web_metadata.get("web_sources", []),
    }

    return PreparedGeneration(
        response=result.get("response"),
        metadata=metadata,
        raw_result=result,
        full_response=[],
    )


async def iterate_response_chunks(response: Any) -> AsyncIterator[str]:
    if inspect.isasyncgen(response):
        async for chunk in response:
            yield normalize_chunk(chunk)
        return

    if inspect.isgenerator(response):
        sentinel = object()

        def next_chunk():
            try:
                return next(response)
            except StopIteration:
                return sentinel

        while True:
            chunk = await asyncio.to_thread(next_chunk)
            if chunk is sentinel:
                return
            yield normalize_chunk(chunk)
        return

    if response is not None:
        yield normalize_chunk(response)


async def stream_generation(
    payload: ChatGenerationRequest,
    cancel_event: asyncio.Event | None = None,
) -> AsyncIterator[dict[str, Any]]:
    prepared = prepare_generation(payload)
    yield {"type": "metadata", "payload": prepared.metadata}

    try:
        async for text_chunk in iterate_response_chunks(prepared.response):
            if cancel_event and cancel_event.is_set():
                raise GenerationCancelled("stream cancelled")
            if text_chunk:
                prepared.full_response.append(text_chunk)
                yield {"type": "token", "payload": {"text": text_chunk}}

        yield {"type": "completion", "payload": {"reason": "completed"}}
    except GenerationCancelled:
        yield {"type": "cancelled", "payload": {"reason": "cancelled"}}
    except Exception as exc:
        yield {"type": "error", "payload": {"message": str(exc)}}
    finally:
        if prepared.persist_response:
            mem_instance.add_new_response(res=prepared.full_response, username=payload.username)
