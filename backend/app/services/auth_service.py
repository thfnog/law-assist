import jwt
import time
from typing import Optional, Dict
from backend.app.core.config import settings
from backend.app.models.database import User, engine
from sqlmodel import Session, select
import requests

class AuthService:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL # We'll add this to config
        self.supabase_key = settings.SUPABASE_KEY # We'll add this to config
        self.jwt_secret = settings.SUPABASE_JWT_SECRET # Required to verify tokens

    def sign_in(self, email: str, password: str) -> Optional[Dict]:
        """Signs in via Supabase Auth and returns user info + token."""
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": self.supabase_key,
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Fetch user profile from our public.user table
            with Session(engine) as session:
                statement = select(User).where(User.id == data["user"]["id"])
                user = session.exec(statement).first()
                
                if user:
                    return {
                        "access_token": data["access_token"],
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "role": user.role,
                            "escritorio_id": user.escritorio_id
                        }
                    }
            return None
        except Exception as e:
            print(f"Auth Error: {e}")
            return None

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verifies a JWT token using Supabase secret."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"], audience="authenticated")
            return payload
        except Exception as e:
            print(f"Token Verification Error: {e}")
            return None

auth_service = AuthService()
