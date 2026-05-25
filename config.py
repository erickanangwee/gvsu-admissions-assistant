"""
Centralized configuration. All modules import from here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY  = os.getenv('ANTHROPIC_API_KEY')
SERPER_API_KEY     = os.getenv('SERPER_API_KEY')
DATABASE_URL       = os.getenv('DATABASE_URL', 'sqlite:///./gvsu_chatbot.db')

LLM_MODEL          = 'claude-sonnet-4-6'
LLM_MAX_TOKENS     = 1024
MAX_SEARCH_RESULTS = 5        # number of search results to fetch and read
MAX_PAGE_CHARS     = 6000     # max characters extracted from each page
MAX_CONVERSATION_TURNS = 10

SEARCH_SITE        = 'gvsu.edu'
SERPER_SEARCH_URL  = 'https://google.serper.dev/search'

API_HOST           = '0.0.0.0'
API_PORT           = 8000