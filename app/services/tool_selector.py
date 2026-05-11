import json
import re
from typing import Any

from services import tavily_client
from services.mistral_client import query_mistral_stream

TOOLS = {
    "search": tavily_client.search,
    "extract": tavily_client.extract,
    "crawl": tavily_client.crawl,
}

TOOL_SELECTION_MODEL = "open-mistral-nemo"

_SELECTION_INSTRUCTION = """You select exactly one Tavily tool for a web agent.
Return only valid JSON with this shape:
{"tool": "search|extract|crawl", "args": {...}, "reason": "..."}

Tool rules:
- search: use for general web queries, news, facts, discovery, latest information.
- extract: use only when the user provides one or more URLs and asks for page contents or details.
- crawl: use only when the user provides one website/root URL and asks to inspect multiple linked pages.

Argument rules:
- search args: {"query": "...", "max_results": 2}
- extract args: {"urls": ["https://..."], "query": "..."}
- crawl args: {"url": "https://...", "instructions": "..."}
"""


def select_tool(query: str) -> dict[str, Any]:
    prompt = f"User request:\n{query}\n\nSelect the best Tavily tool."
    raw = "".join(
        query_mistral_stream(
            prompt=prompt,
            model=TOOL_SELECTION_MODEL,
            instruction=_SELECTION_INSTRUCTION,
            temperature=0,
            top_p=1,
            max_output_token=500,
        )
    )

    selection = _parse_selection(raw)
    return _normalize_selection(selection, query)


def run_selected_tool(query: str) -> dict[str, Any]:
    selection = select_tool(query)
    tool_name = selection["tool"]
    args = selection["args"]
    result = TOOLS[tool_name](**args)

    return {
        "tool": tool_name,
        "args": args,
        "reason": selection.get("reason"),
        "result": result,
    }


def _parse_selection(raw: str) -> dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


def _normalize_selection(selection: dict[str, Any], query: str) -> dict[str, Any]:
    tool = selection.get("tool")
    if tool not in TOOLS:
        tool = "search"

    args = selection.get("args")
    if not isinstance(args, dict):
        args = {}

    urls = _extract_urls(query)
    if tool == "extract":
        normalized_args = {
            "urls": args.get("urls") or urls,
            "query": args.get("query") or query,
        }
        if not normalized_args["urls"]:
            tool = "search"
            normalized_args = {"query": query, "max_results": tavily_client.DEFAULT_MAX_RESULTS}
        args = normalized_args
    elif tool == "crawl":
        normalized_args = {
            "url": args.get("url") or (urls[0] if urls else None),
            "instructions": args.get("instructions") or query,
        }
        if not normalized_args["url"]:
            tool = "search"
            normalized_args = {"query": query, "max_results": tavily_client.DEFAULT_MAX_RESULTS}
        args = normalized_args
    else:
        tool = "search"
        args = {
            "query": args.get("query") or query,
            "max_results": _safe_max_results(args.get("max_results")),
        }

    return {
        "tool": tool,
        "args": args,
        "reason": selection.get("reason"),
    }


def _extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s,)]+", text)


def _safe_max_results(value: Any) -> int:
    try:
        max_results = int(value or tavily_client.DEFAULT_MAX_RESULTS)
    except (TypeError, ValueError):
        return tavily_client.DEFAULT_MAX_RESULTS
    return min(max(max_results, 1), tavily_client.DEFAULT_MAX_RESULTS)
