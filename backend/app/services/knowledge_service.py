import openai
import pandas as pd
from docx import Document
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.core.config import settings
from backend.app.models.database import KnowledgeChunk, engine
from sqlmodel import Session, select
from pgvector.sqlalchemy import Vector
import json
import base64
import io

class KnowledgeService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    def get_embedding(self, text):
        """Generates embedding for a given text using OpenAI."""
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small" # 1536 dimensions
        )
        return response.data[0].embedding

    def parse_pdf(self, file_content):
        """Extracts text from PDF."""
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def parse_docx(self, file_content):
        """Extracts text from DOCX."""
        doc = Document(io.BytesIO(file_content))
        return "\n".join([para.text for para in doc.paragraphs])

    def parse_xlsx(self, file_content):
        """Extracts tabular data from XLSX."""
        df = pd.read_excel(io.BytesIO(file_content))
        return df.to_string()

    def parse_image_ocr(self, file_content):
        """Extracts text from image using GPT-4o Vision."""
        base64_image = base64.b64encode(file_content).decode('utf-8')
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this legal document image. Maintain the structure as much as possible."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content

    def ingest_file(self, file_name, file_content, mime_type, metadata):
        """Parses, splits, embeds and stores file content."""
        text = ""
        if "pdf" in mime_type:
            text = self.parse_pdf(file_content)
        elif "word" in mime_type or "docx" in mime_type:
            text = self.parse_docx(file_content)
        elif "sheet" in mime_type or "xlsx" in mime_type:
            text = self.parse_xlsx(file_content)
        elif "image" in mime_type:
            text = self.parse_image_ocr(file_content)
        
        if not text:
            return

        chunks = self.text_splitter.split_text(text)
        
        with Session(engine) as session:
            for chunk in chunks:
                embedding = self.get_embedding(chunk)
                new_chunk = KnowledgeChunk(
                    content=chunk,
                    metadata_json=json.dumps({**metadata, "file_name": file_name}),
                    embedding=embedding
                )
                session.add(new_chunk)
            session.commit()

    def similarity_search(self, query, limit=5):
        """Finds most relevant knowledge chunks."""
        query_embedding = self.get_embedding(query)
        
        with Session(engine) as session:
            # Using pgvector L2 distance operator (<->) or Cosine distance (<=>)
            # SQLAlchemy/SQLModel syntax for pgvector:
            statement = select(KnowledgeChunk).order_by(KnowledgeChunk.embedding.l2_distance(query_embedding)).limit(limit)
            results = session.exec(statement).all()
            return results

knowledge_service = KnowledgeService()
