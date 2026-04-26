from langchain_groq import ChatGroq
from backend.app.core.config import settings
from backend.app.models.database import Lead, engine
from sqlmodel import Session, select
import json
from langchain_core.messages import HumanMessage

class CRMService:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY, 
            model=settings.GROQ_MODEL_NAME
        )

    def extract_lead_info(self, text: str):
        """Uses AI to extract legal lead information from a message."""
        prompt = f"""
        You are an AI intake assistant for a Brazilian law firm.
        Analyze the following message and extract lead information if relevant.
        
        MESSAGE: "{text}"
        
        EXTRACT:
        - name: string
        - legal_area: 'Trabalhista', 'Cível', 'Família', 'Criminal', 'Previdenciário', 'Empresarial', 'Outros'
        - urgency: 'low', 'medium', 'high'
        - is_lead: boolean (True if it's a potential legal client, False if it's noise/social)
        - summary: brief summary of the legal issue
        
        Return ONLY a JSON object.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            data = json.loads(response.content.replace('```json', '').replace('```', '').strip())
            return data
        except Exception as e:
            print(f"Error in CRMService AI extraction: {e}")
            return {"is_lead": False}

    def save_lead(self, phone: str, lead_data: dict):
        """Saves a qualified lead to the database."""
        with Session(engine) as session:
            # Check if lead already exists by phone
            statement = select(Lead).where(Lead.phone == phone)
            existing_lead = session.exec(statement).first()
            
            if existing_lead:
                existing_lead.status = "qualified"
                existing_lead.legal_area = lead_data.get("legal_area", existing_lead.legal_area)
                existing_lead.summary = lead_data.get("summary", existing_lead.summary)
                session.add(existing_lead)
            else:
                new_lead = Lead(
                    name=lead_data.get("name", "Desconhecido"),
                    phone=phone,
                    legal_area=lead_data.get("legal_area"),
                    urgency=lead_data.get("urgency", "medium"),
                    summary=lead_data.get("summary"),
                    status="qualified"
                )
                session.add(new_lead)
            session.commit()

crm_service = CRMService()
