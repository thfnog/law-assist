import requests
from backend.app.core.config import settings

class WhatsAppTool:
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance = settings.EVOLUTION_INSTANCE_NAME

    def send_message(self, number, text):
        """Sends a text message via Evolution API."""
        # Sanitize number (Evolution API expects 5511...)
        clean_number = "".join(filter(str.isdigit, number))
        
        url = f"{self.base_url}/message/sendText/{self.instance}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        payload = {
            "number": clean_number,
            "text": text
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return {"error": str(e)}

whatsapp_tool = WhatsAppTool()
