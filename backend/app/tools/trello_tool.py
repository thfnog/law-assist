import requests
from backend.app.core.config import settings

class TrelloTool:
    def __init__(self):
        self.api_key = settings.TRELLO_API_KEY
        self.token = settings.TRELLO_TOKEN
        self.base_url = "https://api.trello.com/1"
        self.auth_params = {
            'key': self.api_key,
            'token': self.token
        }

    def create_card(self, name, desc="", list_id=None):
        """Creates a card on Trello (with Demo fallback)."""
        target_list_id = list_id or settings.TRELLO_LIST_ID_CLIENTS
        url = f"{self.base_url}/cards"
        params = {
            **self.auth_params,
            'idList': target_list_id,
            'name': name,
            'desc': desc
        }
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                "id": data["id"],
                "url": data["shortUrl"],
                "name": data["name"]
            }
        except Exception:
            # DEMO MODE FALLBACK
            return {
                "id": "demo_trello_id",
                "url": "https://trello.com/c/demo-card",
                "name": name
            }
        
    def search_card(self, query):
        """Searches for cards by name (with Demo fallback)."""
        url = f"{self.base_url}/search"
        params = {
            **self.auth_params,
            'query': query,
            'modelTypes': 'cards',
            'boardId': settings.TRELLO_BOARD_ID,
            'card_fields': 'name,shortUrl,desc'
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("cards", [])
        except Exception:
            return []

    def get_cards_from_list(self, list_id):
        """Fetches all cards from a specific Trello list."""
        url = f"{self.base_url}/lists/{list_id}/cards"
        try:
            response = requests.get(url, params=self.auth_params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Trello get_cards error: {e}")
            return []

    def move_card(self, card_id, new_list_id):
        """Moves a card to a different list."""
        url = f"{self.base_url}/cards/{card_id}"
        params = {
            **self.auth_params,
            'idList': new_list_id
        }
        try:
            response = requests.put(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Trello move_card error: {e}")
            return None

trello_tool = TrelloTool()
