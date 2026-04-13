import os
from typing import Dict,List,Any
from tavily import TavilyClient
from googleapiclient.discovery import build

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def extract_items_from_tavily(result:Dict[str,Any],limit:int=4)->List[Dict[str,str]]:
    """Cleans Raw Tavily results into the structured Lists"""
    items =[]
    for row in (result or {}).get("results",[])[:limit]:
        url = row.get("url")
        if url:
            items.append({
                "title":row.get("title") or url,
                "url":url,
                "snippet":(row.get("content") or "")[:260]
            })

    return items

def youtube_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """Hybrid search using YouTube API with Tavily fallback."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key:
        try:
            yt = build("youtube", "v3", developerKey=api_key)
            req = yt.search().list(q=query, part="snippet", maxResults=max_results, type="video", safeSearch="moderate")
            res = req.execute()
            out = []
            for item in res.get("items", []):
                vid = item["id"].get("videoId")
                if vid:
                    out.append({
                        "title": item["snippet"].get("title", "YouTube video"),
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "snippet": item["snippet"].get("description", "")[:260],
                    })
            if out: return out
        except Exception:
            pass
    
    tav = tavily_client.search(f"site:youtube.com {query}", search_depth="basic")
    return extract_items_from_tavily(tav, limit=max_results)       


