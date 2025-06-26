import asyncio
import httpx
import importlib
from async_logger import wis_logger

# The unified search entry for every engine under `engines/`.
# Signature is kept consistent with `search_with_jina`, with an extra
# `engine` argument specifying which engine implementation to use.
async def search_with_engine(engine: str, query: str, existings: set[str] = set(), **kwargs) -> list[dict]:
    """Search given *query* with the specified *engine*.

    Parameters
    ----------
    engine : str
        Name of the engine module under ``engines`` folder.
    query : str
        Search query string.
    existings : set[str], optional
        URLs that have already been collected – duplicates will be skipped.

    Returns
    -------
    list[dict]
        A list of search result dictionaries.
    """
    # --- locate engine implementation ------------------------------------------------
    try:
        engine_module = importlib.import_module(f"wis.searchengines.engines.{engine}")
    except ImportError as e:
        wis_logger.error(f"Engine '{engine}' not found: {e}")
        return "", {}

    max_retries = 3
    base_delay = 10  # seconds

    for attempt in range(max_retries):
        try:
            # Build HTTP request from engine implementation
            request_params = await engine_module.request(query, **kwargs)

            if not request_params:
                wis_logger.warning(f"Engine '{engine}' returned invalid request parameters: {request_params}")
                return "", {}

            if "url" not in request_params:
                wis_logger.warning(f"Engine '{engine}' returned invalid request parameters: {request_params}")
                return "", {}

            method = request_params.get("method", "GET").upper()
            url = request_params["url"]
            headers = request_params.get("headers")
            cookies = request_params.get("cookies")

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(method, url, headers=headers, cookies=cookies, timeout=30)

            if response.status_code != 200:
                raise httpx.HTTPStatusError("Unexpected status", request=None, response=response)

            # Parse response
            items = await engine_module.parse_response(response.text, **kwargs)

            return items

        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                wis_logger.warning(
                    f"{engine} search attempt {attempt + 1} failed with error: {str(e)}, retrying in {delay} seconds"
                )
                await asyncio.sleep(delay)
            else:
                wis_logger.error(
                    f"{engine} search failed after {max_retries} attempts with error: {str(e)}"
                )
                return []

    return []
