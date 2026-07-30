from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Summary(Base):
    """
    SQLAlchemy model representing the 'summaries' table in PostgreSQL.
    Stores the original text provided by the user and the AI-generated summary.
    """
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    original_text = Column(String, nullable=False)
    summary_text = Column(String, nullable=False)
    
    # We delegate the timestamp generation directly to the PostgreSQL engine
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

    