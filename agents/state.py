from typing import TypedDict, List, Dict, Any

class PolicyPilotState(TypedDict):
    # Input
    user_input: str
    
    # Parsed Profile (Intake Agent)
    profile: Dict[str, Any]
    
    # Retrieved Clauses (Retrieval Agent)
    retrieved_clauses: List[Dict[str, Any]]
    
    # Eligibility (Eligibility Agent)
    eligibility_results: List[Dict[str, Any]]
    
    # Conflicts (Conflict Detection Agent)
    conflicts: List[Dict[str, Any]]
    
    # Form fields from OCR (Form-Fill Agent)
    extracted_form_fields: Dict[str, Any]
    
    # Final localized response (Response Agent)
    final_output: str
