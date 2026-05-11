from typing import Any

from services.tool_selector import run_selected_tool


def enrich_prompt_with_web(prompt: str) -> tuple[str, dict[str, Any]]:
    tool_response = run_selected_tool(prompt)
    web_context = _format_web_context(tool_response)

    enriched_prompt = f"""Use the web context below to answer the user. Cite source URLs when using web facts.

Web context:
{web_context}

User prompt:
{prompt}
"""

    metadata = {
        "web_used": True,
        "web_tool": tool_response.get("tool"),
        "web_tool_reason": tool_response.get("reason"),
        "web_sources": _collect_sources(tool_response.get("result")),
    }
    return enriched_prompt, metadata


def _format_web_context(tool_response: dict[str, Any]) -> str:
    result = tool_response.get("result")

    if isinstance(result, dict):
        return _format_result_list(result.get("results", [])) or "No web results returned."

    return str(result)


def _format_result_list(results: list[dict[str, Any]], content_key: str = "content") -> str:
    formatted = []
    for index, item in enumerate(results[:8], start=1):
        title = item.get("title") or "Untitled"
        url = item.get("url") or "No URL"
        content = item.get(content_key) or item.get("raw_content") or item.get("content") or ""
        formatted.append(
            f"[{index}] {title}\nURL: {url}\nContent: {_trim(content)}"
        )
    return "\n\n".join(formatted)


def _collect_sources(result: Any) -> list[dict[str, str]]:
    if not isinstance(result, dict):
        return []

    results = []
    if "results" in result:
        results.extend(result.get("results") or [])

    seen = set()
    sources = []
    for item in results:
        url = item.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        sources.append({"title": item.get("title") or url, "url": url})
    return sources


def _trim(text: str, limit: int = 1800) -> str:
    clean = " ".join(str(text).split())
    if len(clean) <= limit:
        return clean
    return f"{clean[:limit].rsplit(' ', 1)[0]}..."
