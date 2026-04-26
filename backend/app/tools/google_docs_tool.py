import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from backend.app.core.config import settings
from datetime import datetime

class GoogleDocsTool:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive'
        ]
        self.service_account_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        self.creds = None
        
        if os.path.exists(self.service_account_file):
            self.creds = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=self.scopes
            )
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)
        else:
            self.docs_service = None
            self.drive_service = None

    def generate_contract(self, client_name, target_folder_id):
        """Generates a contract (with Demo fallback)."""
        if not self.docs_service or not settings.GOOGLE_DOCS_CONTRACT_TEMPLATE_ID:
            return {"id": "demo_doc_id", "url": f"https://docs.google.com/demo/contract-{client_name}", "name": f"Contrato - {client_name}"}

        try:
            template_id = settings.GOOGLE_DOCS_CONTRACT_TEMPLATE_ID
            title = f"Contrato de Honorários - {client_name}"

            # 1. Copy template
            copy_metadata = {
                'name': title,
                'parents': [target_folder_id]
            }
            copied_file = self.drive_service.files().copy(
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

            self.docs_service.documents().batchUpdate(
                documentId=doc_id, body={'requests': requests}
            ).execute()

            return {
                "id": doc_id,
                "url": f"https://docs.google.com/document/d/{doc_id}/edit",
                "name": title
            }
        except Exception:
            return {"id": "demo_doc_id", "url": f"https://docs.google.com/demo/contract-{client_name}", "name": f"Contrato - {client_name}"}

docs_tool = GoogleDocsTool()
