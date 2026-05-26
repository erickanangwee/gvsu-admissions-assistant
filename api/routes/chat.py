"""Chat endpoint."""
import time, logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.models    import ChatRequest, ChatResponse, Source
from api.database  import get_db, QueryLog
from api import answer_engine

log    = logging.getLogger(__name__)
router = APIRouter(prefix='/api/v1')


@router.post('/chat', response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    t0      = time.time()
    history = [{'role': t.role, 'content': t.content} for t in req.history]

    result     = answer_engine.answer(req.message, history, req.topic)
    latency_ms = (time.time() - t0) * 1000

    db.add(QueryLog(
        session_id    = req.session_id,
        query         = req.message,
        answer        = result.answer,
        topic         = req.topic,
        pages_fetched = result.pages_fetched,
        fallback      = result.fallback,
        latency_ms    = latency_ms,
    ))
    db.commit()

    return ChatResponse(
        answer        = result.answer,
        sources       = [Source(**s) for s in result.sources],
        session_id    = req.session_id,
        pages_fetched = result.pages_fetched,
        fallback      = result.fallback,
    )