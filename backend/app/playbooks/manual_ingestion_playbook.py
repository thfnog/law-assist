from backend.app.tools.google_drive_tool import drive_tool
from backend.app.services.knowledge_service import knowledge_service
from backend.app.graph.state import AgentState

def manual_ingestion_playbook(state: AgentState) -> AgentState:
    """Manually indexes files from a specific client or folder."""
    entities = state.get("entities", {})
    client_name = entities.get("client_name")
    
    if not client_name:
        state["result"] = "De qual cliente ou pasta você gostaria de indexar os documentos?"
        return state
    
    # Simple search for folder by name
    # In a real app, we'd search the DB for the client's drive_folder_id
    from backend.app.models.database import Client, engine
    from sqlmodel import Session, select
    
    folder_id = None
    with Session(engine) as session:
        statement = select(Client).where(Client.name.like(f"%{client_name}%"))
        client = session.exec(statement).first()
        if client:
            folder_id = client.drive_folder_id
            
    if not folder_id:
        state["result"] = f"Não encontrei o registro do cliente '{client_name}' no banco. Por favor, verifique o nome."
        return state

    files = drive_tool.list_files_in_folder(folder_id)
    count = 0
    for file in files:
        file_id = file['id']
        file_name = file['name']
        mime_type = file['mimeType']
        
        content = b""
        if "google-apps" in mime_type:
            # Export Google Docs/Sheets
            if "document" in mime_type:
                content = drive_tool.export_file(file_id, 'application/pdf')
                mime_type = "application/pdf"
            elif "spreadsheet" in mime_type:
                content = drive_tool.export_file(file_id, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            content = drive_tool.download_file(file_id)
            
        if content:
            knowledge_service.ingest_file(
                file_name=file_name,
                file_content=content,
                mime_type=mime_type,
                metadata={"client_name": client_name, "source": "drive"}
            )
            count += 1

    state["result"] = f"🚀 Indexação concluída para '{client_name}'! Processados {count} arquivos da pasta do Google Drive."
    return state
