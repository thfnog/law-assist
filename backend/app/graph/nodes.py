from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from backend.app.graph.state import AgentState
from backend.app.core.config import settings
import json

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY, 
    model=settings.GROQ_MODEL_NAME
)

def intent_detector(state: AgentState) -> AgentState:
    """Detects user intent and extracts entities."""
    user_input = state["user_input"]
    
    prompt = f"""
    Analyze the follow user message and extracts the intent and entities.
    Intents: 
    - 'onboarding' (create new client)
    - 'search' (find client/process info in DB/Trello)
    - 'research' (ask questions about documents, contracts, or legal context)
    - 'ingest' (index or sync documents from a client folder)
    - 'finance' (recording payments, honorários, or asking about financial status)
    - 'lead' (initial triage of a new potential client)
    
    User Message: "{user_input}"
    
    Return ONLY a JSON object with:
    {{
        "intent": "onboarding" | "search" | "other",
        "entities": {{
            "client_name": "...",
            "process_number": "..."
        }}
    }}
    """
    
    try:
        response = llm.invoke([SystemMessage(content="You are a legal assistant bot."), HumanMessage(content=prompt)])
        data = json.loads(response.content.replace('```json', '').replace('```', '').strip())
        state["intent"] = data.get("intent")
        state["entities"] = data.get("entities", {})
    except Exception as e:
        print(f"LLM Error: {e}. Using heuristic fallback.")
        # Very simple heuristic for demo validation
        text = user_input.lower()
        if "criar" in text or "onboard" in text or "novo" in text:
            state["intent"] = "onboarding"
            # Try to extract name after 'cliente'
            import re
            match = re.search(r"cliente\s+([A-Za-z\s]+)", text)
            if match:
                state["entities"] = {"client_name": match.group(1).strip()}
        elif "buscar" in text or "pesquisar" in text or "procurar" in text:
            state["intent"] = "search"
            import re
            match = re.search(r"(?:buscar|pesquisar|procurar)\s+([A-Za-z0-9\s]+)", text)
            if match:
                state["entities"] = {"client_name": match.group(1).strip()}
        elif "indexar" in text or "sincronizar" in text:
            state["intent"] = "ingest"
            import re
            match = re.search(r"(?:indexar|sincronizar|pasta)\s+([A-Za-z0-9\s]+)", text)
            if match:
                state["entities"] = {"client_name": match.group(1).strip()}
        elif "o que diz" in text or "quais" in text or "contrato" in text:
            state["intent"] = "research"
        elif "pagamento" in text or "recebi" in text or "honorário" in text or "custas" in text:
            state["intent"] = "finance"
        else:
            state["intent"] = "other"
        
    return state

from backend.app.services.crm_service import crm_service

def lead_qualifier(state: AgentState) -> AgentState:
    """Nodes that qualifies new contacts as leads using AI."""
    user_input = state["user_input"]
    phone = state.get("phone", "unknown") # We should pass this from the API/Webhook
    
    lead_data = crm_service.extract_lead_info(user_input)
    
    if lead_data.get("is_lead"):
        crm_service.save_lead(phone, lead_data)
        state["result"] = f"📋 Lead qualificado com sucesso!\nÁrea: {lead_data.get('legal_area')}\nUrgência: {lead_data.get('urgency')}\nResumo: {lead_data.get('summary')}\n\nO que deseja fazer agora? (Agendar consulta ou Onboarding)"
    else:
        state["result"] = "Olá! Como posso ajudar o escritório hoje?"
        
    return state

from backend.app.models.database import Transaction, engine, Client
from sqlmodel import Session, select

def financial_manager(state: AgentState) -> AgentState:
    """Handles financial requests like recording payments."""
    user_input = state["user_input"]
    
    # Simple extraction for demo purposes
    # In a real app, use LLM to extract amount and client
    import re
    amount_match = re.search(r"(?:R\$|r\$|\$)\s?(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s?(?:reais|reais)", user_input)
    client_match = re.search(r"de\s+([A-Za-z\s]+)|para\s+([A-Za-z\s]+)", user_input)
    
    if amount_match:
        amount = float(amount_match.group(1) or amount_match.group(2))
        client_name = client_match.group(1).strip() if client_match else "Desconhecido"
        
        with Session(engine) as session:
            # Try to find client
            statement = select(Client).where(Client.name.like(f"%{client_name}%"))
            client = session.exec(statement).first()
            
            new_transaction = Transaction(
                client_id=client.id if client else None,
                type="income",
                category="honorarios",
                amount=amount,
                description=f"Pagamento registrado via chat: {user_input}"
            )
            session.add(new_transaction)
            session.commit()
            
        state["result"] = f"💰 Pagamento de R$ {amount:.2f} registrado com sucesso para {client_name}!"
    else:
        state["result"] = "Não consegui identificar o valor ou o cliente para registrar o financeiro. Pode repetir?"
        
    return state

from backend.app.services.knowledge_service import knowledge_service

def knowledge_retriever(state: AgentState) -> AgentState:
    """Searches the knowledge base and injects context into the result."""
    user_input = state["user_input"]
    escritorio_id = state.get("escritorio_id")
    results = knowledge_service.similarity_search(escritorio_id, user_input)
    
    if results:
        context = "\n\n".join([f"--- Contexto de {json.loads(r.metadata_json).get('file_name', 'Documento')}: ---\n{r.content}" for r in results])
        # Use LLM to answer based on context
        prompt = f"""
        Answer the following request using ONLY the provided context from our legal documents.
        If the answer is not in the context, say you don't know based on the files.
        Always mention the file name you are referencing.
        
        Context:
        {context}
        
        Request: "{user_input}"
        """
        response = llm.invoke([SystemMessage(content="You are a legal assistant based on the firm's private documents."), HumanMessage(content=prompt)])
        state["result"] = response.content
    else:
        state["result"] = "Não encontrei informações relevantes nos documentos indexados para responder a essa pergunta."
        
    return state
