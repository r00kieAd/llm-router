import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SEARCH_DEPTH = "basic"
DEFAULT_MAX_RESULTS = 2


def _client():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found")

    from tavily import TavilyClient

    return TavilyClient(api_key)


def search(
    query: str,
    search_depth: str = DEFAULT_SEARCH_DEPTH,
    max_results: int = DEFAULT_MAX_RESULTS,
    include_answer: bool = False,
    include_images: bool = False,
    **kwargs: Any,
) -> dict:
    if not query:
        raise ValueError("query is required for Tavily search")

    return _client().search(
        query=query,
        search_depth=search_depth,
        max_results=max_results,
        include_answer=include_answer,
        include_images=include_images,
        **kwargs,
    )


def extract(
    urls: list[str],
    query: str | None = None,
    extract_depth: str = DEFAULT_SEARCH_DEPTH,
    include_images: bool = False,
    max_results: int = DEFAULT_MAX_RESULTS,
    **kwargs: Any,
) -> dict:
    if not urls:
        raise ValueError("urls is required for Tavily extract")

    request = {
        "urls": urls[:max_results],
        "extract_depth": extract_depth,
        "include_images": include_images,
        **kwargs,
    }
    if query:
        request["query"] = query

    return _client().extract(**request)


def crawl(
    url: str,
    instructions: str = "Extract the most relevant page content for answering the user request.",
    extract_depth: str = DEFAULT_SEARCH_DEPTH,
    max_depth: int = 1,
    limit: int = DEFAULT_MAX_RESULTS,
    **kwargs: Any,
) -> dict:
    if not url:
        raise ValueError("url is required for Tavily crawl")

    return _client().crawl(
        url=url,
        instructions=instructions,
        extract_depth=extract_depth,
        max_depth=max_depth,
        limit=limit,
        **kwargs,
    )
