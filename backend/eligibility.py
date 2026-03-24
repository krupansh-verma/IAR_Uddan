"""
YojnaAI — Core Eligibility Matching Engine
Extracted from frontend logic into a proper Python module.
Uses scheme data from data/schemes.json and conflict rules from data/conflicts.json.
"""

import re
import json
import os
from typing import Dict, List, Any, Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Ministry contact lookup by scheme category
MINISTRY_CONTACTS = {
    "agriculture": {"ministry": "Ministry of Agriculture & Farmers Welfare", "helpline": "1800-180-1551", "email": "agri-helpline@gov.in"},
    "health": {"ministry": "Ministry of Health & Family Welfare", "helpline": "1800-180-1104", "email": "nhm-helpline@gov.in"},
    "education": {"ministry": "Ministry of Education", "helpline": "1800-111-001", "email": "webmaster.edu@gov.in"},
    "housing": {"ministry": "Ministry of Housing & Urban Affairs", "helpline": "1800-11-3377", "email": "pmay-helpline@gov.in"},
    "employment": {"ministry": "Ministry of Labour & Employment", "helpline": "1800-11-0039", "email": "shramsuvidha@gov.in"},
    "women": {"ministry": "Ministry of Women & Child Development", "helpline": "181", "email": "wcd-helpline@gov.in"},
    "senior": {"ministry": "Ministry of Social Justice & Empowerment", "helpline": "1800-180-5222", "email": "msje-helpline@gov.in"},
    "disability": {"ministry": "Ministry of Social Justice & Empowerment", "helpline": "1800-180-5129", "email": "depwd-helpline@gov.in"},
    "finance": {"ministry": "Ministry of Finance", "helpline": "1800-11-0001", "email": "mof-helpline@gov.in"},
    "rural": {"ministry": "Ministry of Rural Development", "helpline": "1800-180-6763", "email": "mord-helpline@gov.in"},
    "business": {"ministry": "Ministry of MSME", "helpline": "1800-180-6763", "email": "msme-helpline@gov.in"},
    "startup": {"ministry": "Ministry of Commerce & Industry (Startup India)", "helpline": "1800-115-565", "email": "dipp-startups@gov.in"},
    "scholarships": {"ministry": "Ministry of Education (Scholarship Division)", "helpline": "0120-6619540", "email": "helpdesk@nsp.gov.in"},
    "food": {"ministry": "Ministry of Consumer Affairs & Food Distribution", "helpline": "1800-11-0841", "email": "pds-helpline@gov.in"},
    "land": {"ministry": "Ministry of Rural Development (Land Resources)", "helpline": "1800-180-6763", "email": "dolr-helpline@gov.in"},
    "immigration": {"ministry": "Ministry of External Affairs", "helpline": "1800-11-3090", "email": "mea-helpline@gov.in"},
    "insurance": {"ministry": "Ministry of Finance (Insurance)", "helpline": "1800-11-0001", "email": "insurance-helpline@gov.in"},
    "loan": {"ministry": "Ministry of Finance (Banking)", "helpline": "1800-11-0001", "email": "banking-helpline@gov.in"},
    "subsidy": {"ministry": "Ministry of Finance (Expenditure)", "helpline": "1800-11-0001", "email": "subsidy-helpline@gov.in"},
    "pension": {"ministry": "Ministry of Labour & Employment (EPFO)", "helpline": "1800-118-005", "email": "epfigms-helpline@gov.in"},
}
DEFAULT_MINISTRY = {"ministry": "Ministry of Social Justice & Empowerment", "helpline": "1800-180-5222", "email": "msje-helpline@gov.in"}


def load_schemes() -> List[Dict[str, Any]]:
    """Load scheme corpus from data/schemes.json."""
    with open(os.path.join(DATA_DIR, "schemes.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["schemes"]


def load_conflict_rules() -> List[Dict[str, Any]]:
    """Load conflict detection rules from data/conflicts.json."""
    with open(os.path.join(DATA_DIR, "conflicts.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["conflictRules"]


def load_pdf_registry() -> List[Dict[str, Any]]:
    """Load PDF source registry from data/pdf_registry.json."""
    with open(os.path.join(DATA_DIR, "pdf_registry.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["pdfSources"]


def parse_profile(text: str, income: float = 0, state: str = "", category: str = "", caste: str = "") -> Dict[str, Any]:
    """
    Parse citizen input text to extract profile fields.
    
    Args:
        text: Free-text citizen description
        income: Annual income in INR
        state: State of residence
        category: Need category filter
        caste: Caste/Community from dropdown (General, OBC, SC/ST, EWS)
    
    Returns:
        Dict with parsed profile
    """
    lower = text.lower()

    # Age extraction
    age_match = (
        re.search(r'age\s*(\d+)', text, re.IGNORECASE)
        or re.search(r'(\d+)[\-\s]*year[s]?-old', text, re.IGNORECASE)
        or re.search(r'(\d+)\s*yo', text, re.IGNORECASE)
        or re.search(r'(\d+)', text)
    )
    age = int(age_match.group(1)) if age_match else 0

    # Income
    income_val = float(str(income).replace(",", "")) if income else 0
    income_str = f"₹{income_val:,.0f}" if income_val > 0 else "Not specified"

    # State
    resolved_state = state if state else "Unspecified"
    if resolved_state == "Unspecified":
        states_list = [
            "gujarat", "maharashtra", "punjab", "haryana", "karnataka",
            "tamil nadu", "bihar", "bengal", "kerala", "odisha",
            "rajasthan", "uttar pradesh", "madhya pradesh"
        ]
        for s in states_list:
            if s in lower:
                resolved_state = s.title()
                break

    # Land / acres
    land_match = re.search(r'(\d+[\.,\d]*)\s*(acre|hectare|एकड|હેકર)', lower)
    acres = float(land_match.group(1)) if land_match else 0

    is_farmer = "farmer" in lower or "किसान" in lower or "ખેડૂત" in lower or acres > 0
    is_student = "student" in lower or "छात्र" in lower or "વિદ્યાર્થી" in lower or "study" in lower or "degree" in lower

    # Caste detection logic (Dropdown wins over Text)
    detected_caste = "General"
    if "sc" in lower or "st" in lower or "scheduled caste" in lower or "scheduled tribe" in lower:
        detected_caste = "SC/ST"
    elif "obc" in lower or "other backward" in lower:
        detected_caste = "OBC"
    elif "ews" in lower or "economically weaker" in lower:
        detected_caste = "EWS"
    
    final_caste = caste if caste else detected_caste

    return {
        "age": age,
        "incomeVal": income_val,
        "incomeStr": income_str,
        "state": resolved_state,
        "acres": acres,
        "isFarmer": is_farmer,
        "isStudent": is_student,
        "caste": final_caste,
        "needCategory": category or "All"
    }


def _resolve_state_scheme(scheme: Dict[str, Any], state: str) -> Dict[str, Any]:
    """Replace {state} and {stateCode} placeholders in a state scheme template."""
    resolved: Dict[str, Any] = {}
    state_str = state if state else "XX"
    state_code = (state_str[0] + state_str[1]).upper() if len(state_str) >= 2 else state_str.upper()
    for key, val in scheme.items():
        if isinstance(val, str):
            resolved[key] = val.replace("{state}", state or "State").replace("{stateCode}", state_code)
        elif isinstance(val, list):
            new_list: List[Any] = []
            for item in val:
                if isinstance(item, str):
                    new_list.append(item.replace("{state}", state or "State").replace("{stateCode}", state_code))
                elif isinstance(item, dict):
                    new_list.append({
                        k: v.replace("{state}", state or "State").replace("{stateCode}", state_code) if isinstance(v, str) else v
                        for k, v in item.items()
                    })
                else:
                    new_list.append(item)
            resolved[key] = new_list
        elif isinstance(val, dict):
            resolved[key] = {
                k: v.replace("{state}", state or "State").replace("{stateCode}", state_code) if isinstance(v, str) else v
                for k, v in val.items()
            }
        else:
            resolved[key] = val
    return resolved


def match_schemes(profile: Dict[str, Any], schemes: List[Dict[str, Any]]) -> tuple:
    """
    Match citizen profile against scheme corpus using generic rules.
    """
    matched = []
    warnings = []
    improvements = []

    for scheme in schemes:
        rules = scheme.get("matchRules", {})
        scheme_entry = dict(scheme)
        is_match = True
        reasons = []

        # 1. Occupational Role
        if rules.get("requiresFarmer") and not profile["isFarmer"]:
            is_match = False
        if rules.get("requiresStudent") and not profile["isStudent"]:
            is_match = False

        # 2. Caste
        req_caste = rules.get("requiresCaste")
        if req_caste:
            # Handle multiple castes if provided as string "SC/ST"
            allowed_castes = req_caste.split("/")
            if profile["caste"] not in allowed_castes:
                is_match = False

        # 3. Income (Max)
        max_inc = rules.get("maxIncome")
        if max_inc and profile["incomeVal"] > 0:
            if profile["incomeVal"] > max_inc:
                is_match = False
                warnings.append(
                    f"{scheme['title']} Rejected: Income ({profile['incomeStr']}) > ₹{max_inc:,.0f} limit "
                    f"({scheme.get('clauseRef', 'Rule')}, {scheme.get('pageRef', 'Page')})"
                )

        # 4. Income (Min) - Improvement logic
        min_inc = rules.get("minIncome")
        if min_inc:
            if profile["incomeVal"] < min_inc:
                is_match = False
                improvements.append(
                    f"By declaring a verifiable annual income of at least ₹{min_inc:,.0f}, "
                    f"you could become eligible for {scheme['title']}."
                )
            else:
                reasons.append(f"Income ≥ ₹{min_inc:,.0f}")

        # 5. Land (Max)
        max_acres = rules.get("maxAcres")
        if max_acres and profile["acres"] > max_acres:
            is_match = False
            warnings.append(
                f"{scheme['title']} Rejected: Land ({profile['acres']} acres) > {max_acres} acre limit."
            )

        # 6. State Requirement
        if rules.get("requiresState") and profile["state"] == "Unspecified":
            is_match = False

        # 7. Forced Include / Default Match
        if rules.get("alwaysInclude"):
            is_match = True
        
        if rules.get("defaultMatch") and not (profile["isFarmer"] or profile["isStudent"]):
            is_match = True

        if is_match:
            # Resolve state placeholders if state scheme
            if scheme.get("scope") == "state" or "{state}" in scheme.get("title", ""):
                scheme_entry = _resolve_state_scheme(scheme, profile["state"])
            
            scheme_entry["matchReason"] = f"Criteria Met — {scheme.get('clauseRef', 'General')}, {scheme.get('pageRef', 'Para')}"
            # Inject ministry contact data
            cat = scheme.get("category", "").lower()
            contact = MINISTRY_CONTACTS.get(cat, DEFAULT_MINISTRY)
            scheme_entry["ministry"] = contact["ministry"]
            scheme_entry["helpline"] = contact["helpline"]
            scheme_entry["email"] = contact["email"]
            matched.append(scheme_entry)

    # Filter by need category
    if profile["needCategory"] and profile["needCategory"] != "All":
        matched = [s for s in matched if s.get("category") == profile["needCategory"]]

    # Filter state schemes: remove state-specific schemes if state doesn't match
    if profile["state"] and profile["state"] != "Unspecified":
        matched = [
            s for s in matched
            if not (s.get("scope") == "state" and profile["state"].lower() not in s.get("title", "").lower() and "{state}" not in s.get("title", ""))
        ]

    return matched, warnings, improvements

def rank_top_5_schemes(profile: Dict[str, Any], matched_schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks schemes based on Eligibility Match, Need Relevance, Benefit Value, and Priority Level.
    Returns the top 5, ensuring no more than 2 schemes per category.
    """
    scored = []
    for s in matched_schemes:
        # Default factors
        eligibility_match = 1.0  # Assumed perfect since it passed match_schemes
        
        # Need Relevance
        is_exact_need_match = profile["needCategory"] == s.get("category")
        need_relevance = 1.0 if is_exact_need_match else 0.5
        
        # Benefit Value (Heuristic estimation)
        summary_text = s.get("summary", "").lower()
        if "lakh" in summary_text or "5,00,000" in summary_text or "3,00,000" in summary_text:
            benefit_value = 1.0
        elif "6,000" in summary_text or "5,000" in summary_text:
            benefit_value = 0.6
        else:
            benefit_value = 0.4
            
        # Priority Level (Heuristic based on central vs state constraints)
        priority_level = 1.0 if s.get("scope") == "central" else 0.8
        
        # Calculate Score = (0.4 * Eligibility) + (0.3 * Need) + (0.2 * Benefit) + (0.1 * Priority)
        score = (0.4 * eligibility_match) + (0.3 * need_relevance) + (0.2 * benefit_value) + (0.1 * priority_level)
        
        # Add score to scheme duplicate to avoid mutating original for standard logic
        scheme_data = dict(s)
        scheme_data["ai_score"] = round(score, 2)
        
        # Why relevant string
        if is_exact_need_match:
            why_relevant = f"Directly targets your need in the {s.get('category', 'specific')} sector."
        elif "sc" in profile["caste"].lower() or "obc" in profile["caste"].lower():
            why_relevant = "Prioritizes your demographic and background for immediate impact."
        elif profile["incomeVal"] > 0 and profile["incomeVal"] < 300000:
            why_relevant = "A crucial safety net for lower-income households like yours."
        else:
            why_relevant = "Provides substantial assistance mapped directly to your occupation and location."
            
        scheme_data["ai_why_relevant"] = why_relevant
        scored.append(scheme_data)
        
    # Sort descending
    scored.sort(key=lambda x: x["ai_score"], reverse=True)
    
    # Appy diversity constraint: Max 2 schemes per category
    top5 = []
    category_counts = {}
    
    for s in scored:
        cat = s.get("category", "general")
        count = category_counts.get(cat, 0)
        if count < 2:
            top5.append(s)
            category_counts[cat] = count + 1
        if len(top5) >= 5:
            break
            
    return top5


def detect_conflicts(matched_schemes: List[Dict[str, Any]], conflict_rules: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
    """
    Detect conflicts between matched schemes using clause-level comparison.
    
    Args:
        matched_schemes: List of matched scheme dicts
        conflict_rules: Optional conflict rules (loaded from conflicts.json if not provided)
    
    Returns:
        List of conflict dicts with dual-source PDF citations
    """
    if conflict_rules is None:
        conflict_rules = load_conflict_rules()

    conflicts = []

    # Check each conflict rule
    for rule in conflict_rules:
        central_id = rule["centralSchemeId"]
        state_id = rule["stateSchemeId"]

        central = next((s for s in matched_schemes if s["id"] == central_id), None)
        state = next(
            (s for s in matched_schemes if s["id"] == state_id or s["id"].startswith(state_id.replace("-state", "-"))),
            None
        )

        if central and state:
            # Resolve template placeholders in state clause
            state_pdf = state.get("pdfSource", rule["stateClause"]["pdf"])

            detail = rule["detailTemplate"].format(
                centralPdf=rule["centralClause"]["pdf"],
                centralClause=rule["centralClause"]["clauseRef"],
                centralPage=rule["centralClause"]["page"],
                statePdf=state_pdf,
                stateClause=rule["stateClause"]["clauseRef"],
                statePage=rule["stateClause"]["page"]
            )

            hindi_detail = rule.get("translations", {}).get("hi", "").format(
                centralPdf=rule["centralClause"]["pdf"],
                centralClause=rule["centralClause"]["clauseRef"],
                centralPage=rule["centralClause"]["page"],
                statePdf=state_pdf,
                stateClause=rule["stateClause"]["clauseRef"],
                statePage=rule["stateClause"]["page"]
            )

            conflicts.append({
                "ruleId": rule["ruleId"],
                "type": rule["type"],
                "title": f"⚠️ {rule['name']}",
                "centralSource": {
                    "pdf": rule["centralClause"]["pdf"],
                    "clause": rule["centralClause"]["clauseRef"],
                    "page": rule["centralClause"]["page"],
                    "text": rule["centralClause"]["extractedText"]
                },
                "stateSource": {
                    "pdf": state_pdf,
                    "clause": rule["stateClause"]["clauseRef"],
                    "page": rule["stateClause"]["page"],
                    "text": rule["stateClause"]["extractedText"]
                },
                "contradictions": rule["contradictions"],
                "detail": detail,
                "hindiDetail": hindi_detail
            })

    return conflicts


def generate_summary(profile: Dict[str, Any], schemes: List[Dict[str, Any]], language: str = "en") -> str:
    """Generate plain-language summary of eligibility results."""
    count = len(schemes)
    names = ", ".join(str(s.get("title", s.get("id", "Unknown"))) for s in schemes)

    if language != "en":
        return (
            f"आपकी प्रोफाइल (आयु: {profile['age']}, राज्य: {profile['state']}, "
            f"आय: {profile['incomeStr']}) के आधार पर, आप {count} योजनाओं के लिए पात्र हैं: {names}। "
            f"प्रत्येक योजना पर क्लिक करके विस्तृत जानकारी देखें।"
        )

    return (
        f"Based on your profile (Age: {profile['age']}, State: {profile['state']}, "
        f"Income: {profile['incomeStr']}), you are eligible for {count} scheme(s): {names}. "
        f"Click each scheme for detailed step-by-step instructions, required documents, and office locations."
    )


def analyze(text: str, income: float = 0, state: str = "", category: str = "", language: str = "en", caste: str = "") -> Dict[str, Any]:
    """
    Full analysis pipeline: parse → match → detect conflicts → summarize.
    
    This is the main entry point for the API.
    
    Args:
        text: Citizen input text
        income: Annual income (INR)
        state: State of residence
        category: Need category filter
        language: Language code for summary
        caste: Caste/Community from dropdown
    
    Returns:
        Complete analysis result with profile, schemes, conflicts, warnings, and summary
    """
    schemes = load_schemes()
    profile = parse_profile(text, income, state, category, caste)
    matched, warnings, improvements = match_schemes(profile, schemes)
    conflicts = detect_conflicts(matched)
    summary = generate_summary(profile, matched, language)
    top5 = rank_top_5_schemes(profile, matched)

    return {
        "profile": profile,
        "schemes": matched,
        "conflicts": conflicts,
        "warnings": warnings,
        "improvements": improvements,
        "summary": summary,
        "top5": top5,
        "totalSchemesSearched": len(schemes),
        "matchCount": len(matched)
    }


# --- CLI Test ---
if __name__ == "__main__":
    print("=" * 60)
    print("YojnaAI Eligibility Engine — CLI Test")
    print("=" * 60)

    result = analyze(
        text="I am a 45-year-old farmer with 2 acres of land",
        income=140000,
        state="Gujarat",
        category="agriculture"
    )

    print(f"\nProfile: {json.dumps(result['profile'], indent=2, ensure_ascii=False)}")
    print(f"\nMatched {result['matchCount']} / {result['totalSchemesSearched']} schemes:")
    for s in result["schemes"]:
        print(f"  ✓ {s['title']} — {s.get('matchReason', 'N/A')}")
        print(f"    📄 {s.get('pdfSource', 'N/A')} → {s.get('clauseRef', 'N/A')}, {s.get('pageRef', 'N/A')}")

    if result["conflicts"]:
        print(f"\n🚩 {len(result['conflicts'])} Conflict(s) Detected:")
        for c in result["conflicts"]:
            print(f"  {c['title']}")
            print(f"    CENTRAL: {c['centralSource']['pdf']} → {c['centralSource']['clause']}")
            print(f"    STATE:   {c['stateSource']['pdf']} → {c['stateSource']['clause']}")

    if result["warnings"]:
        print(f"\n⚠️ Warnings: {result['warnings']}")

    if result.get("improvements"):
        print(f"\n🚀 Profile Strengthening Opportunities:")
        for imp in result["improvements"]:
            print(f"  • {imp}")

    print(f"\n📝 Summary: {result['summary']}")
