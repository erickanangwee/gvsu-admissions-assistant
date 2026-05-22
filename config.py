"""
Centralized configuration. All modules import from here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY  = os.getenv('ANTHROPIC_API_KEY')
GOOGLE_API_KEY     = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID      = os.getenv('GOOGLE_CSE_ID')
DATABASE_URL       = os.getenv('DATABASE_URL', 'sqlite:///./gvsu_chatbot.db')

LLM_MODEL          = 'claude-sonnet-4-6'
LLM_MAX_TOKENS     = 1024
MAX_SEARCH_RESULTS = 5        # number of Google results to fetch and read
MAX_PAGE_CHARS     = 6000     # max characters extracted from each page
MAX_CONVERSATION_TURNS = 10

SEARCH_SITE        = 'gvsu.edu'
GOOGLE_SEARCH_URL  = 'https://www.googleapis.com/customsearch/v1'

API_HOST           = '0.0.0.0'
API_PORT           = 8000