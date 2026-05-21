"""SQLAlchemy database setup and query log model."""
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

engine       = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()


class QueryLog(Base):
    __tablename__ = 'query_logs'
    id            = Column(Integer, primary_key=True, index=True)
    session_id    = Column(String(64), index=True)
    query         = Column(Text)
    answer        = Column(Text)
    topic         = Column(String(64), nullable=True)
    pages_fetched = Column(Integer)
    fallback      = Column(Boolean, default=False)
    latency_ms    = Column(Float)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()