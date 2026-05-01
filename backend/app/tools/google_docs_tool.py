from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from backend.app.core.config import settings
from backend.app.models.database import engine
from sqlmodel import Session, text
from datetime import datetime
import json

class GoogleDocsTool:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive'
        ]

    def _get_services(self, escritorio_id: str):
        """Builds Google services using tokens from the database."""
        with Session(engine) as session:
            query = text("SELECT config FROM public.escritorio_integracao WHERE escritorio_id = :esc_id AND provider = 'google'")
            result = session.execute(query, {"esc_id": escritorio_id}).fetchone()
            
            if not result:
                return None, None
            
            config = json.loads(result[0])
            creds = Credentials(
                token=config.get('access_token'),
                refresh_token=config.get('refresh_token'),
                token_uri=config.get('token_uri'),
                client_id=config.get('client_id'),
                client_secret=config.get('client_secret'),
                scopes=config.get('scopes')
            )
            docs_service = build('docs', 'v1', credentials=creds)
            drive_service = build('drive', 'v3', credentials=creds)
            return docs_service, drive_service

    def generate_contract(self, escritorio_id, client_name, target_folder_id):
        """Generates a contract using the office's credentials."""
        docs_service, drive_service = self._get_services(escritorio_id)
        
        if not docs_service or not settings.GOOGLE_DOCS_CONTRACT_TEMPLATE_ID:
            return {"id": "demo_doc_id", "url": f"https://docs.google.com/demo/contract-{client_name}", "name": f"Contrato - {client_name}"}

        try:
            template_id = settings.GOOGLE_DOCS_CONTRACT_TEMPLATE_ID
            title = f"Contrato de Honorários - {client_name}"

            # 1. Copy template
            copy_metadata = {
                'name': title,
                'parents': [target_folder_id]
            }
            copied_file = drive_service.files().copy(
                fileId=template_id, body=copy_metadata
            ).execute()
            doc_id = copied_file.get('id')

            # 2. Replace placeholders
            replacements = [
                {'{{NOME_CLIENTE}}': client_name},
                {'{{DATA}}': datetime.now().strftime("%d/%m/%Y")}
            ]
            
            requests = []
            for replacement in replacements:
                for placeholder, value in replacement.items():
                    requests.append({
                        'replaceAllText': {
                            'containsText': {
                                'text': placeholder,
                                'matchCase': True
                            },
                            'replaceText': value
                        }
                    })

            docs_service.documents().batchUpdate(
                documentId=doc_id, body={'requests': requests}
            ).execute()

            return {
                "id": doc_id,
                "url": f"https://docs.google.com/document/d/{doc_id}/edit",
                "name": title
            }
        except Exception as e:
            print(f"Error in generate_contract: {e}")
            return {"id": "demo_doc_id", "url": f"https://docs.google.com/demo/contract-{client_name}", "name": f"Contrato - {client_name}"}

docs_tool = GoogleDocsTool()
