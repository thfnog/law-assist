import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from backend.app.core.config import settings

class GoogleDriveTool:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.service_account_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE
        self.creds = None
        
        if os.path.exists(self.service_account_file):
            self.creds = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=self.scopes
            )
            self.service = build('drive', 'v3', credentials=self.creds)
        else:
            self.service = None

    def download_file(self, file_id):
        """Downloads a file's content."""
        if not self.service: return b""
        return self.service.files().get_media(fileId=file_id).execute()

    def export_file(self, file_id, mime_type='text/plain'):
        """Exports a Google Doc/Sheet/Slide as a specific mime type."""
        if not self.service: return b""
        return self.service.files().export(fileId=file_id, mimeType=mime_type).execute()

    def list_files_in_folder(self, folder_id):
        """Lists all files in a specific folder."""
        if not self.service: return []
        query = f"'{folder_id}' in parents and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        return results.get('files', [])

    def create_folder(self, folder_name, parent_id=None):
        """Creates a folder in Google Drive (with Demo fallback)."""
        if not self.service or not settings.GOOGLE_DRIVE_PARENT_FOLDER_ID:
            return {"id": "demo_drive_id", "url": f"https://drive.google.com/demo/{folder_name}", "name": folder_name}

        try:
            parent_folder_id = parent_id or settings.GOOGLE_DRIVE_PARENT_FOLDER_ID
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id] if parent_folder_id else []
            }
            file = self.service.files().create(body=file_metadata, fields='id, webViewLink').execute()
            return {
                "id": file.get('id'),
                "url": file.get('webViewLink'),
                "name": folder_name
            }
        except Exception:
            return {"id": "demo_drive_id", "url": f"https://drive.google.com/demo/{folder_name}", "name": folder_name}

drive_tool = GoogleDriveTool()
