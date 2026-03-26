from agents.state import PolicyPilotState  # pyre-ignore[21]
from typing import Dict, Any
import json
import os
from backend.eligibility import analyze, load_schemes

def intake_node(state: PolicyPilotState) -> Dict[str, Any]:
    print("--- INTAKE AGENT ---")
    user_input = state.get("user_input", "")
    # In a real app, an LLM would parse the profile. 
    # Here we use the backend parser for consistency.
    from backend.eligibility import parse_profile
    profile = parse_profile(user_input)
    
    # Allow manual overrides for demo
    if "[INCOME: 5L]" in user_input: profile["incomeVal"] = 500000
    if "[CASTE: SC]" in user_input: profile["caste"] = "SC"
    
    # Check for validation errors
    if profile.get("validationError"):
        print(f"⚠️ VALIDATION ERROR: {profile['validationError']}")
    else:
        print(f"Parsed Profile: {json.dumps(profile, indent=2, ensure_ascii=False)}")
    
    return {"profile": profile}

def retrieval_node(state: PolicyPilotState) -> Dict[str, Any]:
    print("--- RETRIEVAL AGENT ---")
    profile = state.get("profile", {})
    
    # Short-circuit if validation error
    if profile.get("validationError"):
        print("⚠️ Skipping retrieval — invalid input detected.")
        return {"retrieved_clauses": []}
    
    schemes = load_schemes()
    
    # Filter schemes based on broad category if present
    category = profile.get("needCategory", "All")
    retrieved = []
    for s in schemes:
        if category == "All" or s.get("category") == category.lower():
            retrieved.append({
                "scheme_name": s["title"],
                "scope": s["scope"],
                "section_id": s.get("clauseRef", "General"),
                "clause_id": s.get("docId", "N/A"),
                "text": s.get("extractedText", s.get("summary", ""))
            })
    
    # Sort or limit for RAG window
    retrieved = retrieved[:10] 
    print(f"Retrieved {len(retrieved)} relevant policies from corpus.")
    return {"retrieved_clauses": retrieved}

def eligibility_node(state: PolicyPilotState) -> Dict[str, Any]:
    print("--- ELIGIBILITY AGENT ---")
    user_input = state.get("user_input", "")
    profile = state.get("profile", {})
    
    # Short-circuit if validation error
    if profile.get("validationError"):
        print(f"⚠️ 0 schemes matched — {profile['validationError']}")
        return {
            "eligibility_results": [],
            "analysis_output": {
                "profile": profile,
                "schemes": [],
                "conflicts": [],
                "warnings": [profile["validationError"]],
                "improvements": [],
                "summary": profile["validationError"],
                "top5": [],
                "totalSchemesSearched": 0,
                "matchCount": 0,
                "validationError": profile["validationError"]
            }
        }
    
    # Use the REAL eligibility engine
    analysis = analyze(
        text=user_input,
        income=profile.get("incomeVal", 0),
        state=profile.get("state", ""),
        category=profile.get("needCategory", "All")
    )
    
    results = []
    for s in analysis["schemes"]:
        results.append({
            "scheme_name": s["title"],
            "status": "Eligible",
            "reasoning": s.get("matchReason", "Criteria matched based on profile."),
            "clause_ref": s.get("clauseRef", "N/A")
        })
        
    print(f"Eligibility Match Confirmed for {len(results)} schemes.")
    return {"eligibility_results": results, "analysis_output": analysis}

def conflict_detector_node(state: PolicyPilotState) -> Dict[str, Any]:
    print("--- CONFLICT DETECTION AGENT ---")
    analysis = state.get("analysis_output", {})
    conflicts = analysis.get("conflicts", [])
    
    if conflicts:
        print(f"WARNING: {len(conflicts)} Conflict(s) Detected between state and central policies.")
    return {"conflicts": conflicts}

def form_fill_node(state: PolicyPilotState) -> Dict[str, Any]:
    print("--- FORM-FILL AGENT ---")
    extracted = {
        "Aadhaar_Name": {"value": "Ramesh Bhai", "confidence": 0.99, "human_review_flag": False},
        "Aadhaar_DOB": {"value": "1981-05-12", "confidence": 0.98, "human_review_flag": False},
        "Income_Value": {"value": "₹1,40,000", "confidence": 0.82, "human_review_flag": True} 
    }
    print("OCR extraction mapped to application form schema.")
    return {"extracted_form_fields": extracted}

def response_node(state: PolicyPilotState) -> Dict[str, Any]:
    print("--- RESPONSE AGENT ---")
    analysis = state.get("analysis_output", {})
    results = state.get("eligibility_results", [])
    conflicts = state.get("conflicts", [])
    profile = state.get("profile", {})
    
    # Handle validation errors
    if profile.get("validationError") or analysis.get("validationError"):
        error_msg = profile.get("validationError") or analysis.get("validationError")
        output = f"🚫 Input Rejected: {error_msg}\n"
        output += "Please provide valid citizen information to analyze eligibility.\n"
        return {"final_output": output}
    
    if len(results) == 0:
        output = "ℹ️ No schemes matched your profile.\n"
        output += "Try providing more details about your age, occupation, state, and income.\n"
    else:
        output = f"✅ Eligibility Confirmed for {len(results)} schemes.\n"
        output += "Matched policies: " + ", ".join([r["scheme_name"] for r in results]) + "\n"
    
    if conflicts:
        output += f"⚠️ CONFLICT ALERT: {len(conflicts)} policy contradictions detected.\n"
        for c in conflicts:
            output += f" - {c['title']}: {c.get('detail', 'Conflict detected.')}\n"
            
    output += f"\n📝 Summary: {analysis.get('summary', 'Analysis complete.')}\n"
    
    return {"final_output": output}
