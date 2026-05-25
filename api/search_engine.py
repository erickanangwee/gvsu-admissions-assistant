"""
Search engine — replaces the RAG pipeline entirely.
1. Queries Google Custom Search restricted to gvsu.edu
2. Fetches and cleans the top N result pages
3. Returns structured passages with source metadata
"""
import logging
import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from config import (
    SERPER_API_KEY, SERPER_SEARCH_URL,
    MAX_SEARCH_RESULTS, MAX_PAGE_CHARS, SEARCH_SITE
)

log = logging.getLogger(__name__)

_REMOVE_TAGS = ['nav', 'header', 'footer', 'script', 'style',
                 'noscript', 'aside', 'form', 'iframe', 'menu']


@dataclass
class SearchPassage:
    text: str
    title: str
    url: str
    snippet: str   # Google's own snippet for quick context


def _serper_search(query: str) -> list[dict]:
    """
    Call the Serper Google Search API.
    Returns a list of result dicts with keys: title, link, snippet.
    """
    try:
        resp = httpx.post(
            SERPER_SEARCH_URL,
            headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'},
            json={'q': f'site:{SEARCH_SITE} {query}', 'num': MAX_SEARCH_RESULTS},
            timeout=10,
        )
        if not resp.is_success:
            log.error(f'Serper API {resp.status_code}: {resp.text}')
            return []
        return resp.json().get('organic', [])
    except Exception as e:
        log.error(f'Serper API error: {e}')
        return []


def _fetch_page_text(url: str) -> str:
    """
    Fetch a GVSU page and extract clean body text.
    Returns up to MAX_PAGE_CHARS characters.
    """
    try:
        resp = httpx.get(url, timeout=12, follow_redirects=True,
                         headers={'User-Agent': 'GVSU-Chatbot/1.0 (academic project)'})
        resp.raise_for_status()
    except Exception as e:
        log.warning(f'Could not fetch {url}: {e}')
        return ''

    soup = BeautifulSoup(resp.text, 'lxml')

    for tag in soup.find_all(_REMOVE_TAGS):
        tag.decompose()

    main = (soup.find('main') or
            soup.find(id='content') or
            soup.find(class_='main-content') or
            soup.body)

    raw = main.get_text(separator=' ', strip=True) if main else ''
    text = re.sub(r'\s+', ' ', raw).strip()

    return text[:MAX_PAGE_CHARS]


def search_and_fetch(query: str) -> list[SearchPassage]:
    """
    Main entry point.
    1. Searches Google CSE for the query on gvsu.edu
    2. Fetches each result page and extracts clean text
    3. Returns a list of SearchPassage objects (or empty list on failure)
    """
    results = _serper_search(query)
    if not results:
        log.warning(f'No Serper results for query: {query}')
        return []

    passages = []
    for item in results:
        url     = item.get('link', '')
        title   = item.get('title', url)
        snippet = item.get('snippet', '')

        log.info(f'Fetching: {url}')
        text = _fetch_page_text(url)

        if text:
            passages.append(SearchPassage(
                text=text,
                title=title,
                url=url,
                snippet=snippet,
            ))

    log.info(f'Fetched {len(passages)} pages for query: {query!r}')
    return passages