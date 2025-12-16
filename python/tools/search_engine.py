import asyncio
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers import searxng, perplexity_search, models

SEARCH_ENGINE_RESULTS = 10

class SearchEngine(Tool):
    async def execute(self, query="", **kwargs):
        
        # 1. Try Perplexity (Highest Quality if Key exists)
        perplexity_key = models.get_api_key("perplexity")
        if perplexity_key and perplexity_key != "None":
            try:
                # PrintStyle.hint("Searching with Perplexity...")
                result = perplexity_search.perplexity_search(query, api_key=perplexity_key)
                return Response(message=result, break_loop=False)
            except Exception as e:
                PrintStyle.error(f"Perplexity search failed: {e}")

        # 2. Try SearXNG (Standard Agent Zero Tool)
        try:
            # PrintStyle.hint("Searching with local SearXNG...")
            searxng_result = await self.searxng_search(query)
            return Response(message=searxng_result, break_loop=False)
        except Exception as e:
             return Response(message=f"Search providers failed. Ensure SearXNG container is running. Error: {e}", break_loop=False)

    async def searxng_search(self, question):
        results = await searxng.search(question)
        return self.format_result_searxng(results, "Search Engine")

    def format_result_searxng(self, result, source):
        if isinstance(result, Exception) or (isinstance(result, dict) and "error" in result):
            error_msg = str(result.get('error', result)) if isinstance(result, dict) else str(result)
            return f"{source} search failed: {error_msg}"

        if not result or "results" not in result:
            return f"{source} search returned no data."

        outputs = []
        for item in result["results"]:
            outputs.append(f"{item.get('title','')}\n{item.get('url','')}\n{item.get('content','')}")

        return "\n\n".join(outputs[:SEARCH_ENGINE_RESULTS]).strip()
