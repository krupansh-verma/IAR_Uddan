from langgraph.graph import StateGraph, END  # pyre-ignore[21]
from agents.state import PolicyPilotState  # pyre-ignore[21]
from agents.nodes import (
    intake_node,
    retrieval_node,
    eligibility_node,
    conflict_detector_node,
    form_fill_node,
    response_node
)

def build_graph():
    workflow = StateGraph(PolicyPilotState)
    
    # Add Nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("eligibility", eligibility_node)
    workflow.add_node("conflict_detection", conflict_detector_node)
    workflow.add_node("form_fill", form_fill_node)
    workflow.add_node("response", response_node)
    
    # Add Edges (Linear for the demo, though in reality there'd be conditional edges)
    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "retrieval")
    workflow.add_edge("retrieval", "eligibility")
    workflow.add_edge("eligibility", "conflict_detection")
    workflow.add_edge("conflict_detection", "form_fill")
    workflow.add_edge("form_fill", "response")
    workflow.add_edge("response", END)
    
    return workflow.compile()

if __name__ == "__main__":
    app = build_graph()
    test_input = "I am a 45-year-old farmer in Gujarat, with 2 acres of land and income of ₹1,40,000."
    print(f"Testing Graph with input: {test_input}\\n")
    
    result = app.invoke({"user_input": test_input})
    print("\\n=== FINAL STATE ===")
    print(result["final_output"])
