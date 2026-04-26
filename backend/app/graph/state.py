from typing import TypedDict, Optional, List, Dict

class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    entities: Dict[str, str]
    result: Optional[str]
    client_data: Optional[Dict]
    links: Dict[str, str]
    history: List[str]
    phone: Optional[str]
