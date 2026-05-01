import json
from google_auth_oauthlib.flow import Flow
from backend.app.core.config import settings
from backend.app.models.database import engine
from sqlmodel import Session, text
from fastapi import HTTPException

class GoogleAuthService:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/documents'
        ]
        # These should be in settings/env
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = f"{settings.APP_URL}/api/auth/google/callback"

    def get_authorization_url(self, escritorio_id: str):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        # State can include the escritorio_id
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=escritorio_id
        )
        return authorization_url

    def handle_callback(self, code: str, escritorio_id: str):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Save to database
        config = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        with Session(engine) as session:
            query = text("""
                INSERT INTO public.escritorio_integracao (escritorio_id, provider, config)
                VALUES (:esc_id, 'google', :config)
                ON CONFLICT (escritorio_id, provider) 
                DO UPDATE SET config = :config, updated_at = NOW()
            """)
            session.execute(query, {"esc_id": escritorio_id, "config": json.dumps(config)})
            session.commit()
            
        return {"status": "success"}

google_auth_service = GoogleAuthService()
