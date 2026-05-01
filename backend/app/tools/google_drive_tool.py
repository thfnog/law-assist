from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from backend.app.core.config import settings
from backend.app.models.database import engine
from sqlmodel import Session, text
import json

class GoogleDriveTool:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/documents'
        ]

    def _get_service(self, escritorio_id: str):
        """Builds a Google Drive service using tokens from the database."""
        with Session(engine) as session:
            query = text("SELECT config FROM public.escritorio_integracao WHERE escritorio_id = :esc_id AND provider = 'google'")
            result = session.execute(query, {"esc_id": escritorio_id}).fetchone()
            
            if not result:
                return None
            
            config = json.loads(result[0])
            creds = Credentials(
                token=config.get('access_token'),
                refresh_token=config.get('refresh_token'),
                token_uri=config.get('token_uri'),
                client_id=config.get('client_id'),
                client_secret=config.get('client_secret'),
                scopes=config.get('scopes')
            )
            return build('drive', 'v3', credentials=creds)

    def download_file(self, escritorio_id, file_id):
        """Downloads a file's content."""
        service = self._get_service(escritorio_id)
        if not service: return b""
        return service.files().get_media(fileId=file_id).execute()

    def export_file(self, escritorio_id, file_id, mime_type='text/plain'):
        """Exports a Google Doc/Sheet/Slide as a specific mime type."""
        service = self._get_service(escritorio_id)
        if not service: return b""
        return service.files().export(fileId=file_id, mimeType=mime_type).execute()

    def list_files_in_folder(self, escritorio_id, folder_id):
        """Lists all files in a specific folder."""
        service = self._get_service(escritorio_id)
        if not service: return []
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        return results.get('files', [])

    def create_folder(self, escritorio_id, folder_name, parent_id=None):
        """Creates a folder in Google Drive."""
        service = self._get_service(escritorio_id)
        if not service:
            return {"id": "demo_drive_id", "url": f"https://drive.google.com/demo/{folder_name}", "name": folder_name}

        try:
            parent_folder_id = parent_id or settings.GOOGLE_DRIVE_PARENT_FOLDER_ID
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id] if parent_folder_id else []
            }
            file = service.files().create(body=file_metadata, fields='id, webViewLink').execute()
            return {
                "id": file.get('id'),
                "url": file.get('webViewLink'),
                "name": folder_name
            }
        except Exception:
            return {"id": "demo_drive_id", "url": f"https://drive.google.com/demo/{folder_name}", "name": folder_name}

drive_tool = GoogleDriveTool()
