"""FastAPI entry point. Run: uvicorn api.main:app --reload"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database    import init_db
from api.routes.chat import router as chat_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title='GVSU Admissions Chatbot', version='2.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'https://your-production-domain.com'],
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event('startup')
def startup():
    init_db()

app.include_router(chat_router)