from langgraph.graph import StateGraph, END
from backend.app.graph.state import AgentState
from backend.app.graph.nodes import intent_detector, knowledge_retriever, lead_qualifier, financial_manager
from backend.app.playbooks.onboarding_playbook import onboarding_playbook
from backend.app.playbooks.search_playbook import search_playbook
from backend.app.playbooks.manual_ingestion_playbook import manual_ingestion_playbook

def route_by_intent(state: AgentState):
    """Router function to decide which node to call next."""
    intent = state.get("intent")
    if intent == "onboarding":
        return "onboarding"
    elif intent == "search":
        return "search"
    elif intent == "research":
        return "research"
    elif intent == "ingest":
        return "ingest"
    elif intent == "lead":
        return "lead"
    elif intent == "finance":
        return "finance"
    else:
        return END

def create_workflow():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("intent_detector", intent_detector)
    workflow.add_node("onboarding", onboarding_playbook)
    workflow.add_node("search", search_playbook)
    workflow.add_node("research", knowledge_retriever)
    workflow.add_node("ingest", manual_ingestion_playbook)
    workflow.add_node("lead", lead_qualifier)
    workflow.add_node("finance", financial_manager)

    # Edges
    workflow.set_entry_point("intent_detector")
    workflow.add_conditional_edges(
        "intent_detector",
        route_by_intent,
        {
            "onboarding": "onboarding",
            "search": "search",
            "research": "research",
            "ingest": "ingest",
            "lead": "lead",
            "finance": "finance",
            "end": END
        }
    )
    workflow.add_edge("onboarding", END)
    workflow.add_edge("search", END)
    workflow.add_edge("research", END)
    workflow.add_edge("ingest", END)
    workflow.add_edge("lead", END)
    workflow.add_edge("finance", END)

    return workflow.compile()

app_graph = create_workflow()
