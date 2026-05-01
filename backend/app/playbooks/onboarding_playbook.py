from backend.app.tools.trello_tool import trello_tool
from backend.app.tools.google_drive_tool import drive_tool
from backend.app.tools.google_docs_tool import docs_tool
from backend.app.models.database import Client, engine
from sqlmodel import Session
from backend.app.graph.state import AgentState

def onboarding_playbook(state: AgentState) -> AgentState:
    """Executes the client onboarding workflow."""
    entities = state.get("entities", {})
    client_name = entities.get("client_name")
    
    escritorio_id = state.get("escritorio_id")
    
    if not client_name:
        state["result"] = "Poderia informar o nome do cliente?"
        return state
    
    try:
        # 1. Trello
        trello_res = trello_tool.create_card(client_name, desc=f"Client onboarding for {client_name}")
        
        # 2. Drive
        drive_res = drive_tool.create_folder(escritorio_id, client_name)
        
        # 3. Google Docs (Contract)
        docs_res = docs_tool.generate_contract(escritorio_id, client_name, drive_res["id"])
        
        # 4. Database
        with Session(engine) as session:
            new_client = Client(
                escritorio_id=escritorio_id,
                name=client_name,
                phone=state.get("phone", "unknown"),
                trello_card_id=trello_res["id"],
                drive_folder_id=drive_res["id"],
                contract_doc_id=docs_res["id"],
                contract_doc_url=docs_res["url"]
            )
            session.add(new_client)
            session.commit()
            session.refresh(new_client)

        # 5. Auto-indexing (RAG)
        try:
            from backend.app.services.knowledge_service import knowledge_service
            # We download the exported contract (PDF) and ingest it
            contract_content = drive_tool.export_file(escritorio_id, docs_res["id"], 'application/pdf')
            knowledge_service.ingest_file(
                escritorio_id=escritorio_id,
                file_name=f"Contrato_{client_name}.pdf",
                file_content=contract_content,
                mime_type="application/pdf",
                metadata={"client_name": client_name, "source": "auto_onboarding"}
            )
        except Exception as e:
            print(f"Auto-indexing failed: {e}")

        state["links"] = {
            "trello": trello_res["url"],
            "drive": drive_res["url"],
            "contract": docs_res["url"]
        }
        state["result"] = f"✅ Cliente {client_name} registrado com sucesso!\n(O contrato já foi indexado na base de conhecimento)\n\n📋 Trello: {trello_res['url']}\n📂 Google Drive: {drive_res['url']}\n📄 Contrato: {docs_res['url']}"
        
    except Exception as e:
        print(f"Error in onboarding_playbook: {e}")
        state["result"] = f"Erro ao processar onboarding: {str(e)}"
        
    return state
