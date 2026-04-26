from backend.app.tools.trello_tool import trello_tool
from backend.app.models.database import Client, engine
from sqlmodel import Session, select
from backend.app.graph.state import AgentState

def search_playbook(state: AgentState) -> AgentState:
    """Searches for client or process information."""
    entities = state.get("entities", {})
    query = entities.get("client_name") or entities.get("process_number")
    
    if not query:
        state["result"] = "O que você gostaria de pesquisar?"
        return state
    
    results = []
    
    # 1. Database Search
    try:
        with Session(engine) as session:
            statement = select(Client).where(Client.name.like(f"%{query}%"))
            db_clients = session.exec(statement).all()
            for client in db_clients:
                results.append(f"👤 {client.name}\n   - Trello: {client.trello_card_url}\n   - Drive: {client.drive_folder_url}\n")
    except Exception as e:
        print(f"DB search error: {e}")

    # 2. Trello Search (fallback/secondary)
    try:
        if not results:
            trello_cards = trello_tool.search_card(query)
            for card in trello_cards:
                results.append(f"📋 {card['name']} (Trello)\n   - Link: {card['shortUrl']}\n")
    except Exception as e:
        print(f"Trello search error: {e}")

    if results:
        state["result"] = "Encontrei estas informações:\n\n" + "\n".join(results)
    else:
        state["result"] = f"Não encontrei resultados para '{query}'."
        
    return state
