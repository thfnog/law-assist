from fastapi import APIRouter, Request, BackgroundTasks
from backend.app.graph.workflow import app_graph
from backend.app.tools.whatsapp_tool import whatsapp_tool
from backend.app.graph.state import AgentState

router = APIRouter()

from backend.app.services.auth_service import auth_service
from pydantic import BaseModel
from fastapi import HTTPException

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/login")
async def login(data: LoginRequest):
    result = auth_service.sign_in(data.email, data.password)
    if result:
        return result
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message")
    
    initial_state: AgentState = {
        "user_input": message,
        "intent": None,
        "entities": {},
        "result": None,
        "client_data": None,
        "links": {},
        "history": []
    }
    
    config = {"configurable": {"thread_id": "1"}}
    final_state = await app_graph.ainvoke(initial_state, config=config)
    
    return {"response": final_state.get("result", "Desculpe, não entendi.")}

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook for Evolution API."""
    data = await request.json()
    
    # Evolution API sends specific events. We look for 'messages.upsert'
    event = data.get("event")
    if event == "messages.upsert":
        msg_data = data.get("data", {})
        message_content = msg_data.get("message", {})
        
        # Get text from different possible locations in the JSON
        text = message_content.get("conversation") or \
               message_content.get("extendedTextMessage", {}).get("text")
        
        sender = msg_data.get("key", {}).get("remoteJid")
        
        if text and sender:
            # Run the agent in background to not block the webhook
            background_tasks.add_task(process_whatsapp_message, sender, text)
            
    return {"status": "received"}

async def process_whatsapp_message(sender: str, text: str):
    """Processes a message received via WhatsApp."""
    # Extract phone from JID (e.g. 5511999999999@s.whatsapp.net -> 5511999999999)
    phone = sender.split("@")[0] if "@" in sender else sender
    
    initial_state = {
        "user_input": text,
        "intent": None,
        "entities": {},
        "result": None,
        "client_data": None,
        "links": {},
        "history": [],
        "phone": phone
    }
    
    final_state = await app_graph.ainvoke(initial_state)
    response_text = final_state.get("result", "Desculpe, não entendi seu pedido.")
    
    # Send response back to user
    whatsapp_tool.send_message(sender, response_text)
