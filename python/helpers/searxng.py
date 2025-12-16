import aiohttp
from python.helpers import runtime

async def search(query):
    # This wrapper ensures the call works in both Docker and Bare Metal modes
    return await runtime.call_development_function(_search, query=query)

async def _search(query):
    # Base URL for local SearXNG instance (container port 8080 mapped to 55510)
    url = "http://localhost:55510/search"
    
    # Parameters to force JSON output and set language
    params = {
        "q": query,
        "format": "json",
        "language": "en",
        "safesearch": "0"
    }
    
    # Headers to mimic a real browser and bypass 403 Forbidden checks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                # Check for HTTP errors
                if response.status != 200:
                    text = await response.text()
                    return {"error": f"SearXNG returned status {response.status}", "details": text[:200]}
                
                # Parse JSON
                data = await response.json()
                return data
                
    except Exception as e:
        return {"error": "Failed to connect to SearXNG. Is the Docker container running?", "details": str(e)}
