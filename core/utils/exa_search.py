import httpx

headers = {
    "x-api-key": "",
    "Content-Type": "application/json"
}

def search_with_exa(query: str) -> str:
    url = "https://api.exa.ai/search"
    
    payload = {
        "query": query,
        "useAutoprompt": True,
        "type": "auto",
        "category": "news",
        "numResults": 5,
        "startCrawlDate": "2024-12-01T00:00:00.000Z",
        "endCrawlDate": "2025-01-21T00:00:00.000Z",
        "startPublishedDate": "2024-12-01T00:00:00.000Z", 
        "endPublishedDate": "2025-01-21T00:00:00.000Z",
        "contents": {
            "text": {
                "maxCharacters": 1000,
                "includeHtmlTags": False
            },
            "livecrawl": "always",
        }
    }
    
    response = httpx.post(url, json=payload, headers=headers, timeout=30)
    return response.text