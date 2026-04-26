from sqlmodel import SQLModel, Field, create_engine, Session, select, Column
from sqlalchemy import text
from pgvector.sqlalchemy import Vector
from datetime import datetime
from typing import Optional
from backend.app.core.config import settings

class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    trello_card_id: Optional[str] = None
    trello_card_url: Optional[str] = None
    drive_folder_id: Optional[str] = None
    drive_folder_url: Optional[str] = None
    contract_doc_id: Optional[str] = None
    contract_doc_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="active") # active, closed, archived

class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str = Field(index=True)
    legal_area: Optional[str] = None
    urgency: str = Field(default="medium") # low, medium, high
    summary: Optional[str] = None
    status: str = Field(default="new") # new, qualified, discarded, converted
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")
    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")
    type: str # income, expense
    category: str # honorarios, custas, outros
    amount: float
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    metadata_json: str  # Extra info (source file, client name, etc)
    embedding: list[float] = Field(sa_column=Column(Vector(1536))) # OpenAI dimension
    created_at: datetime = Field(default_factory=datetime.utcnow)

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

import time

def create_db_and_tables():
    """Initializes the database with retries for Docker synchronization."""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # Enable pgvector extension before creating tables
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                
            SQLModel.metadata.create_all(engine)
            print("Successfully connected to the database and initialized pgvector!")
            return
        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to the database.")
                raise e

def get_session():
    with Session(engine) as session:
        yield session
