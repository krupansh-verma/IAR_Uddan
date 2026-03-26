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


def _detect_absurd_input(text: str) -> Optional[str]:
    """
    Detect nonsensical, fraudulent, or absurd citizen inputs.
    Returns a rejection reason string if absurd, None if input seems legitimate.
    """
    lower = text.lower().strip()

    # 1. Too short to be meaningful (less than 5 real words)
    words = [w for w in lower.split() if len(w) > 1]
    if len(words) < 2:
        return "Input too short. Please describe your situation in detail (age, occupation, state, income)."

    # 2. Death / deceased indicators
    death_keywords = [
        "i am dead", "i'm dead", "i died", "i have died", "deceased",
        "passed away", "no longer alive", "not alive", "ghost", "zombie",
        "i am a ghost", "dead person", "mrit", "मृत", "मर गया", "मैं मर",
    ]
    for kw in death_keywords:
        if kw in lower:
            return "Invalid input: A deceased person cannot apply for welfare schemes."

    # 3. Non-human / joke inputs
    joke_keywords = [
        "i am a dog", "i am a cat", "i am an animal", "i am alien",
        "i am robot", "i am god", "i am superman", "i am batman",
        "i am a tree", "i am a stone", "i am a rock",
    ]
    for kw in joke_keywords:
        if kw in lower:
            return "Invalid input: Please provide genuine information about a real citizen."

    # 4. Gibberish detection — if text has NO recognizable profile keywords at all
    profile_signals = [
        "year", "old", "age", "income", "farmer", "student", "worker",
        "born", "live", "state", "city", "village", "acres", "land",
        "family", "house", "job", "employ", "business", "women", "woman",
        "girl", "boy", "man", "child", "senior", "pension", "help",
        "scheme", "benefit", "pregnant", "widow", "disable", "health",
        "education", "school", "college", "salary", "rupee", "rs", "₹",
        "lakh", "thousand", "crore", "monthly", "annual", "yearly",
        "किसान", "ખેડૂત", "छात्र", "આવક", "उम्र", "राज्य",
        "gujarat", "maharashtra", "bihar", "punjab", "karnataka",
        "tamil", "kerala", "odisha", "rajasthan", "uttar", "madhya",
        "haryana", "bengal", "assam", "jharkhand", "chhattisgarh",
        "sc", "st", "obc", "ews", "general", "caste", "tribe",
        "category", "कैटगरी", "ration", "bpl", "apl",
    ]
    has_signal = any(sig in lower for sig in profile_signals)
    if not has_signal:
        return "Could not understand your input. Please describe your age, occupation, state, and income."

    return None


def _extract_age_from_text(text: str) -> int:
    """
    Extract age from text using smart, context-aware regex.
    Handles: 'age 45', '45-year-old', '45 years old', '45 yo',
    'born on 20/11/2005', 'DOB: 1980-05-12', etc.
    Does NOT use a generic \\d+ fallback.
    """
    lower = text.lower()

    # 1. Explicit age mentions: "age 45", "age is 45", "aged 45"
    m = re.search(r'\bage[d]?\s*(?:is\s*)?(\d{1,3})\b', text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # 2. "X-year-old", "X year old", "X years old"
    m = re.search(r'\b(\d{1,3})\s*[-\s]?\s*year[s]?\s*[-\s]?\s*old\b', text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # 3. "X yo"
    m = re.search(r'\b(\d{1,3})\s*yo\b', text, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # 4. DOB: DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    m = re.search(r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2026:
            from datetime import date
            try:
                dob = date(year, month, day)
                today = date(2026, 3, 26)  # Current date
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return max(age, 0)
            except ValueError:
                pass

    # 5. DOB: YYYY-MM-DD (ISO format)
    m = re.search(r'\b(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})\b', text)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2026:
            from datetime import date
            try:
                dob = date(year, month, day)
                today = date(2026, 3, 26)
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                return max(age, 0)
            except ValueError:
                pass

    # 6. "I am X" where X is a number in age-plausible range and followed by nothing suspicious
    # Only match if the number is between 1 and 120 and not part of an income/land context
    m = re.search(r'\bi\s+am\s+(?:a\s+)?(\d{1,3})\b', text, re.IGNORECASE)
    if m:
        val = int(m.group(1))
        if 1 <= val <= 120:
            return val

    # NO generic \d+ fallback — return 0 if we can't determine age
    return 0


def _extract_income_from_text(text: str) -> float:
    """
    Extract income from natural language text.
    Handles: '₹1,40,000', 'Rs 1.4 lakh', 'income of 140000', '2.5 lakh', '50,000 per month', etc.
    """
    lower = text.lower()

    # 1. Indian format: ₹1,40,000 or Rs. 1,40,000 or INR 1,40,000
    m = re.search(r'[₹]?\s*(?:rs\.?\s*|inr\s*)?(\d{1,3}(?:,\d{2,3})*(?:\.\d+)?)\s*(?:per\s*(?:year|annum|annual))?', lower)
    if m:
        val_str = m.group(1).replace(",", "")
        val = float(val_str)
        # Check if "per month" or "monthly"
        context_after = lower[m.end():m.end()+30]
        if "per month" in context_after or "monthly" in context_after or "mahina" in context_after:
            val = val * 12
        if val >= 1000:  # Only if it looks like income, not age
            return val

    # 2. Lakh format: "1.4 lakh", "2 lakhs", "₹1.5 lakh"
    m = re.search(r'[₹]?\s*(?:rs\.?\s*|inr\s*)?(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)\b', lower)
    if m:
        return float(m.group(1)) * 100000

    # 3. Thousand format: "50 thousand", "50k"
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:thousand|k|हज़ार)\b', lower)
    if m:
        val = float(m.group(1)) * 1000
        context_before = lower[:m.start()]
        if "per month" in context_before or "monthly" in context_before:
            val = val * 12
        return val

    # 4. Explicit "income of X" or "income ₹X"
    m = re.search(r'income\s*(?:of|is|:)?\s*[₹]?\s*(\d[\d,]*)', lower)
    if m:
        return float(m.group(1).replace(",", ""))

    return 0


def parse_profile(text: str, income: float = 0, state: str = "", category: str = "", caste: str = "") -> Dict[str, Any]:
    """
    Parse citizen input text to extract profile fields with robust validation.

    Args:
        text: Free-text citizen description
        income: Annual income in INR (from form field)
        state: State of residence (from form field)
        category: Need category filter
        caste: Caste/Community from dropdown (General, OBC, SC/ST, EWS)

    Returns:
        Dict with parsed profile. Includes 'validationError' key if input is rejected.
    """
    lower = text.lower()

    # ── 1. Absurd Input Detection ──────────────────────────────────
    rejection = _detect_absurd_input(text)
    if rejection:
        return {
            "age": 0, "incomeVal": 0, "incomeStr": "N/A",
            "state": "Unspecified", "acres": 0,
            "isFarmer": False, "isStudent": False,
            "caste": caste or "General", "needCategory": category or "All",
            "isPregnant": False, "isWidow": False, "isDisabled": False,
            "isSenior": False, "isMinor": False, "isWoman": False,
            "validationError": rejection
        }

    # ── 2. Age Extraction (Smart) ──────────────────────────────────
    age = _extract_age_from_text(text)

    # ── 3. Income (Form field wins, then extract from text) ────────
    income_val = float(str(income).replace(",", "")) if income else 0
    if income_val == 0:
        income_val = _extract_income_from_text(text)
    income_str = f"₹{income_val:,.0f}" if income_val > 0 else "Not specified"

    # ── 4. State Detection ─────────────────────────────────────────
    resolved_state = state if state else "Unspecified"
    if resolved_state == "Unspecified":
        states_list = [
            "andhra pradesh", "arunachal pradesh", "assam", "bihar",
            "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh",
            "jharkhand", "karnataka", "kerala", "madhya pradesh",
            "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland",
            "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
            "telangana", "tripura", "uttar pradesh", "uttarakhand",
            "west bengal", "bengal",
            "delhi", "chandigarh", "jammu", "kashmir", "ladakh",
        ]
        for s in states_list:
            if s in lower:
                resolved_state = s.title()
                break

    # ── 5. Land / Acres ────────────────────────────────────────────
    land_match = re.search(r'(\d+[\.,\d]*)\s*(acre|hectare|एकड|હેકર)', lower)
    acres = float(land_match.group(1).replace(",", ".")) if land_match else 0

    # ── 6. Occupation Detection ────────────────────────────────────
    is_farmer = any(kw in lower for kw in [
        "farmer", "farming", "cultivat", "agriculture", "kisan",
        "किसान", "ખેડૂત", "crop", "harvest",
    ]) or acres > 0

    is_student = any(kw in lower for kw in [
        "student", "study", "studying", "degree", "college", "university",
        "school", "education", "छात्र", "વિદ્યાર્થી", "class", "10th", "12th",
        "graduate", "postgraduate", "engineering", "medical",
    ])

    # ── 7. Demographic Flags ───────────────────────────────────────
    is_pregnant = any(kw in lower for kw in ["pregnant", "expecting", "गर्भवती", "maternity"])
    is_widow = any(kw in lower for kw in ["widow", "विधवा", "widowed"])
    is_disabled = any(kw in lower for kw in [
        "disabled", "disability", "handicap", "divyang", "pwd",
        "differently abled", "विकलांग", "दिव्यांग",
    ])
    is_woman = any(kw in lower for kw in [
        "woman", "women", "female", "girl", "lady", "mahila", "महिला",
    ]) or is_pregnant or is_widow
    is_senior = age >= 60 if age > 0 else any(kw in lower for kw in [
        "senior", "elderly", "old age", "retired", "pension", "वृद्ध",
    ])
    is_minor = 0 < age < 18

    # ── 8. Caste Detection (Dropdown wins over Text) ───────────────
    detected_caste = "General"
    # Use word-boundary check to avoid false positives (e.g. "school" matching "sc")
    if re.search(r'\bsc\b', lower) or re.search(r'\bst\b', lower) or "scheduled caste" in lower or "scheduled tribe" in lower:
        detected_caste = "SC/ST"
    elif re.search(r'\bobc\b', lower) or "other backward" in lower:
        detected_caste = "OBC"
    elif re.search(r'\bews\b', lower) or "economically weaker" in lower:
        detected_caste = "EWS"

    # Check for [CATEGORY: ...] tag appended by app.py
    cat_match = re.search(r'\[CATEGORY:\s*([^\]]+)\]', text, re.IGNORECASE)
    if cat_match:
        tag_caste = cat_match.group(1).strip()
        if tag_caste and tag_caste != "General":
            detected_caste = tag_caste

    final_caste = caste if caste else detected_caste

    # ── 9. Age Validation (STRICT) ─────────────────────────────────
    validation_warnings: List[str] = []
    if age > 120:
        validation_warnings.append(f"Age {age} seems unrealistic. Please verify.")
        age = 0

    # HARD REJECT: Children under 5 cannot hold Aadhaar, ration card, or any
    # government document. They are ineligible for ALL schemes.
    if 0 < age < 5:
        return {
            "age": age, "incomeVal": income_val, "incomeStr": income_str,
            "state": resolved_state, "acres": 0,
            "isFarmer": False, "isStudent": False,
            "caste": final_caste, "needCategory": category or "All",
            "isPregnant": False, "isWidow": False, "isDisabled": False,
            "isSenior": False, "isMinor": True, "isWoman": is_woman,
            "validationError": (
                f"A {age}-year-old child cannot apply for government schemes. "
                "Children under 5 do not have Aadhaar cards, ration cards, or any "
                "government identity documents required for scheme enrollment. "
                "If you are a parent/guardian, please enter YOUR details to find "
                "schemes for your family (e.g., maternity benefits, child health schemes)."
            )
        }

    # Children 5-13: too young for most schemes, only guardian-applied health/food
    if 5 <= age <= 13:
        validation_warnings.append(
            f"Age {age}: Only child health and nutrition schemes are applicable. "
            "Most government schemes require the applicant to be at least 14 years old with valid ID."
        )
        is_farmer = False
        is_student = False  # Pre-14 students can't apply for post-matric scholarships

    # Minors (14-17) cannot be farmers
    if is_minor and is_farmer:
        validation_warnings.append("A minor (under 18) cannot be a registered farmer. Farmer schemes will not match.")
        is_farmer = False

    return {
        "age": age,
        "incomeVal": income_val,
        "incomeStr": income_str,
        "state": resolved_state,
        "acres": acres,
        "isFarmer": is_farmer,
        "isStudent": is_student,
        "caste": final_caste,
        "needCategory": category or "All",
        "isPregnant": is_pregnant,
        "isWidow": is_widow,
        "isDisabled": is_disabled,
        "isSenior": is_senior,
        "isMinor": is_minor,
        "isWoman": is_woman,
        "validationWarnings": validation_warnings,
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
    Match citizen profile against scheme corpus using context-aware rules.
    Now includes age-awareness, demographic matching, and prevents blind matching.
    """
    matched = []
    warnings = []
    improvements = []

    age = profile.get("age", 0)
    is_minor = profile.get("isMinor", False)
    has_meaningful_profile = (
        profile.get("isFarmer") or profile.get("isStudent") or
        profile.get("incomeVal", 0) > 0 or age > 0 or
        profile.get("isPregnant") or profile.get("isWidow") or
        profile.get("isDisabled") or profile.get("isSenior") or
        profile.get("state", "Unspecified") != "Unspecified"
    )

    for scheme in schemes:
        rules = scheme.get("matchRules", {})
        scheme_entry = dict(scheme)
        is_match = True
        reasons = []

        # ── 1. Occupational Role ──
        if rules.get("requiresFarmer") and not profile["isFarmer"]:
            is_match = False
        if rules.get("requiresStudent") and not profile["isStudent"]:
            is_match = False

        # ── 2. Caste ──
        req_caste = rules.get("requiresCaste")
        if req_caste:
            allowed_castes = req_caste.split("/")
            user_caste = profile.get("caste", "General")
            # SC/ST dropdown maps to both SC and ST
            user_caste_parts = user_caste.split("/")
            if not any(uc in allowed_castes for uc in user_caste_parts):
                is_match = False

        # ── 3. Income (Max) ──
        max_inc = rules.get("maxIncome")
        if max_inc and profile["incomeVal"] > 0:
            if profile["incomeVal"] > max_inc:
                is_match = False
                warnings.append(
                    f"{scheme['title']} Rejected: Income ({profile['incomeStr']}) > ₹{max_inc:,.0f} limit "
                    f"({scheme.get('clauseRef', 'Rule')}, {scheme.get('pageRef', 'Page')})"
                )

        # ── 4. Income (Min) — Improvement logic ──
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

        # ── 5. Land (Max) ──
        max_acres = rules.get("maxAcres")
        if max_acres and profile["acres"] > max_acres:
            is_match = False
            warnings.append(
                f"{scheme['title']} Rejected: Land ({profile['acres']} acres) > {max_acres} acre limit."
            )

        # ── 6. State Requirement ──
        if rules.get("requiresState") and profile["state"] == "Unspecified":
            is_match = False

        # ── 7. Age-Based Filtering (STRICT) ──
        # Under 5 is hard-rejected in parse_profile, so won't reach here.
        # 5-13: ONLY health/food (guardian-applied child schemes)
        # 14-17: health/food + education/scholarships (post-matric students)
        if is_minor:
            scheme_cat = scheme.get("category", "").lower()
            if age > 0 and age <= 13:
                allowed_cats = ["health", "food"]
            else:
                # 14-17: can apply for education/scholarships with school ID
                allowed_cats = ["health", "food", "education", "scholarships"]
            if scheme_cat not in allowed_cats:
                is_match = False
            # Minors can NEVER be farmers, business owners, pensioners, etc.
            if rules.get("requiresFarmer"):
                is_match = False

        # Seniors: student schemes shouldn't match
        if profile.get("isSenior") and rules.get("requiresStudent"):
            is_match = False

        # ── 7b. Require SOME explicit criterion match for generic schemes ──
        # If a scheme has no strong matchRules (no requiresFarmer, requiresStudent,
        # requiresCaste, maxIncome, minIncome, maxAcres), it should only match
        # if the profile demonstrates concrete relevance (occupation, income, state)
        has_explicit_rules = any(rules.get(k) for k in [
            "requiresFarmer", "requiresStudent", "requiresCaste",
            "maxIncome", "minIncome", "maxAcres", "alwaysInclude", "defaultMatch"
        ])
        if not has_explicit_rules and is_match:
            # Generic scheme: require at least ONE concrete signal
            has_concrete_signal = (
                profile.get("isFarmer") or profile.get("isStudent") or
                profile.get("incomeVal", 0) > 0 or
                profile.get("state", "Unspecified") != "Unspecified" or
                profile.get("isPregnant") or profile.get("isWidow") or
                profile.get("isDisabled") or profile.get("isSenior")
            )
            if not has_concrete_signal:
                is_match = False

        # ── 8. Forced Include / Default Match (NOW with guards) ──
        # alwaysInclude and defaultMatch require a meaningful profile
        if rules.get("alwaysInclude"):
            if has_meaningful_profile and not is_minor:
                is_match = True
            # If profile is empty/absurd, DO NOT force-include

        if rules.get("defaultMatch") and not (profile["isFarmer"] or profile["isStudent"]):
            if has_meaningful_profile and not is_minor:
                is_match = True
            # If profile is empty/absurd, DO NOT default-include

        if is_match:
            # Resolve state placeholders if state scheme
            if scheme.get("scope") == "state" or "{state}" in scheme.get("title", ""):
                scheme_entry = _resolve_state_scheme(scheme, profile["state"])

            # Build a richer match reason
            match_parts = []
            if rules.get("requiresFarmer") and profile["isFarmer"]:
                match_parts.append("Farmer ✓")
            if rules.get("requiresStudent") and profile["isStudent"]:
                match_parts.append("Student ✓")
            if req_caste:
                match_parts.append(f"Caste: {profile.get('caste', 'General')} ✓")
            if max_inc and profile["incomeVal"] > 0:
                match_parts.append(f"Income ≤ ₹{max_inc:,.0f} ✓")
            if reasons:
                match_parts.extend(reasons)
            match_parts.append(f"{scheme.get('clauseRef', 'General')}, {scheme.get('pageRef', 'Para')}")

            scheme_entry["matchReason"] = "Criteria Met — " + " | ".join(match_parts)

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
    Ranks schemes using multi-factor scoring:
    - Eligibility Strength (how many criteria explicitly matched)
    - Need Relevance (category alignment)
    - Benefit Value (monetary heuristic)
    - Priority Level (central vs state)
    - Demographic Bonus (caste, gender, disability, age-group)
    Returns top 5 with max 2 per category for diversity.
    """
    scored = []
    for s in matched_schemes:
        rules = s.get("matchRules", {})

        # ── 1. Eligibility Strength (how explicitly the profile matches) ──
        eligibility_match = 0.5  # Base: it passed the filter
        if rules.get("requiresFarmer") and profile.get("isFarmer"):
            eligibility_match = 1.0
        elif rules.get("requiresStudent") and profile.get("isStudent"):
            eligibility_match = 1.0
        elif rules.get("requiresCaste"):
            eligibility_match = 0.95  # strong caste-targeted match
        elif rules.get("maxIncome") and profile.get("incomeVal", 0) > 0:
            eligibility_match = 0.85  # income was checked and passed

        # ── 2. Need Category Relevance ──
        is_exact_need_match = (
            profile.get("needCategory", "All") != "All" and
            profile["needCategory"] == s.get("category")
        )
        need_relevance = 1.0 if is_exact_need_match else 0.4

        # ── 3. Benefit Value (monetary heuristic from summary) ──
        summary_text = s.get("summary", "").lower()
        if any(kw in summary_text for kw in ["lakh", "5,00,000", "3,00,000", "2,50,000"]):
            benefit_value = 1.0
        elif any(kw in summary_text for kw in ["6,000", "5,000", "10,000", "12,000"]):
            benefit_value = 0.6
        elif "free" in summary_text or "subsid" in summary_text:
            benefit_value = 0.7
        else:
            benefit_value = 0.35

        # ── 4. Priority Level ──
        priority_level = 1.0 if s.get("scope") == "central" else 0.75

        # ── 5. Demographic Bonus ──
        demo_bonus = 0.0
        scheme_cat = s.get("category", "").lower()
        if profile.get("isPregnant") and scheme_cat in ["health", "women"]:
            demo_bonus += 0.3
        if profile.get("isWidow") and scheme_cat in ["women", "pension"]:
            demo_bonus += 0.3
        if profile.get("isDisabled") and scheme_cat == "disability":
            demo_bonus += 0.3
        if profile.get("isSenior") and scheme_cat in ["senior", "pension", "health"]:
            demo_bonus += 0.25
        if profile.get("isMinor") and scheme_cat in ["education", "scholarships"]:
            demo_bonus += 0.2
        caste_lower = profile.get("caste", "General").lower()
        if ("sc" in caste_lower or "st" in caste_lower) and rules.get("requiresCaste"):
            demo_bonus += 0.2
        if "obc" in caste_lower and rules.get("requiresCaste"):
            demo_bonus += 0.15

        # ── Final Score ──
        score = (
            0.30 * eligibility_match +
            0.25 * need_relevance +
            0.15 * benefit_value +
            0.10 * priority_level +
            0.20 * min(demo_bonus, 1.0)  # Cap at 1.0
        )

        scheme_data = dict(s)
        scheme_data["ai_score"] = round(score, 3)

        # ── Build context-aware "Why Relevant" string ──
        why_parts = []
        if is_exact_need_match:
            why_parts.append(f"Directly targets your {s.get('category', '')} needs.")
        if rules.get("requiresFarmer") and profile.get("isFarmer"):
            why_parts.append("Designed specifically for farmers like you.")
        if rules.get("requiresStudent") and profile.get("isStudent"):
            why_parts.append("Built for students to support your education.")
        if rules.get("requiresCaste"):
            why_parts.append(f"Targeted for {profile.get('caste', 'your')} community.")
        if profile.get("incomeVal", 0) > 0 and profile["incomeVal"] < 300000:
            why_parts.append("A critical safety net for lower-income households.")
        if profile.get("isPregnant") and scheme_cat in ["health", "women"]:
            why_parts.append("Maternity support for expecting mothers.")
        if profile.get("isSenior") and scheme_cat in ["senior", "pension"]:
            why_parts.append("Essential support for senior citizens.")
        if not why_parts:
            why_parts.append("Provides valuable assistance for your profile and location.")

        scheme_data["ai_why_relevant"] = " ".join(why_parts[:2])  # Max 2 reasons
        scored.append(scheme_data)

    # Sort descending by score
    scored.sort(key=lambda x: x["ai_score"], reverse=True)

    # Diversity constraint: Max 2 schemes per category
    top5: List[Dict[str, Any]] = []
    category_counts: Dict[str, int] = {}

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
    
    top_names = ", ".join(str(s.get("title", s.get("id", "Unknown"))) for s in schemes[:5])
    if count > 5:
        top_names += f" and {count - 5} others"

    eng_summary = (
        f"Based on your profile (Age: {profile['age']}, State: {profile['state']}, "
        f"Income: {profile['incomeStr']}), you are eligible for {count} scheme(s): {top_names}. "
        f"Click each scheme for detailed step-by-step instructions, required documents, and office locations."
    )

    if language != "en":
        from deep_translator import GoogleTranslator
        try:
            return GoogleTranslator(source='en', target=language).translate(eng_summary)
        except Exception as e:
            print(f"Summary translation error: {e}")
            return eng_summary

    return eng_summary


DOCUMENT_GUIDE = {
    "Aadhaar": {
        "name": "Aadhaar Card",
        "icon": "🪪",
        "url": "https://uidai.gov.in",
        "steps": [
            "Visit your nearest Aadhaar Enrollment Centre or apply online at uidai.gov.in",
            "Fill the enrollment form with personal details and biometrics",
            "Submit required proofs (Identity + Address)",
            "Collect your Aadhaar within 60–90 days via post"
        ],
        "methods": ["Online Download (mAadhaar App)", "Post Delivery", "Nearest Aadhaar Centre"]
    },
    "Ration Card": {
        "name": "Ration Card (NFSA)",
        "icon": "🍚",
        "url": "https://nfsa.gov.in",
        "steps": [
            "Apply online through your state's Food & Civil Supplies portal",
            "Submit Aadhaar, income proof, family details & address proof",
            "An inspector will verify your residence",
            "Card issued within 15–30 working days"
        ],
        "methods": ["State Portal Online", "Nearest Tehsildar Office", "Common Service Centre (CSC)"]
    },
    "Income Certificate": {
        "name": "Income Certificate",
        "icon": "💵",
        "url": "https://serviceonline.gov.in",
        "steps": [
            "Apply on your state's e-District portal or visit Tehsildar office",
            "Submit Aadhaar, salary slips / self-declaration, and address proof",
            "Revenue officer verifies and issues the certificate",
            "Typically issued within 7–15 working days"
        ],
        "methods": ["e-District Portal Online", "Tehsildar / SDM Office", "CSC Centre"]
    },
    "Caste Certificate": {
        "name": "Caste Certificate (SC/ST/OBC)",
        "icon": "📜",
        "url": "https://serviceonline.gov.in",
        "steps": [
            "Apply on e-District or visit your District Magistrate's office",
            "Submit Aadhaar, proof of caste (father's certificate / affidavit)",
            "Field verification by revenue officer",
            "Certificate issued within 15–30 working days"
        ],
        "methods": ["e-District Portal Online", "District Magistrate Office", "CSC Centre"]
    },
    "Bank Passbook": {
        "name": "Bank Account / Passbook",
        "icon": "🏦",
        "url": "https://pmjdy.gov.in",
        "steps": [
            "Visit any nationalized bank branch with Aadhaar + PAN",
            "Request a Jan Dhan (zero-balance) account if eligible",
            "Fill KYC form and submit photographs",
            "Passbook issued instantly on the same day"
        ],
        "methods": ["Any Bank Branch (Walk-in)", "Online (Some Banks)", "Banking Correspondent"]
    },
    "Land Record": {
        "name": "Land Record / Khasra-Khatauni",
        "icon": "🌾",
        "url": "https://dilrmp.gov.in",
        "steps": [
            "Visit your state's Bhulekh / Land Records portal",
            "Enter your district, tehsil, and village to search",
            "Download the certified copy or request a physical copy from Tehsildar",
            "Use for PM-Kisan, KCC, and agricultural scheme applications"
        ],
        "methods": ["State Bhulekh Portal (Online Download)", "Tehsildar / Revenue Office", "CSC Centre"]
    },
    "Disability Certificate": {
        "name": "Disability Certificate (PwD)",
        "icon": "♿",
        "url": "https://swavlambancard.gov.in",
        "steps": [
            "Visit the nearest government hospital's disability assessment board",
            "Get assessed by a medical panel for disability percentage",
            "Submit the assessment report to the Chief Medical Officer (CMO)",
            "UDID card issued within 30 days via Swavlamban portal"
        ],
        "methods": ["UDID Portal Online", "Government Hospital", "District CMO Office"]
    },
    "Domicile Certificate": {
        "name": "Domicile / Residence Certificate",
        "icon": "🏠",
        "url": "https://serviceonline.gov.in",
        "steps": [
            "Apply through e-District portal or Tehsildar office",
            "Submit Aadhaar, voter ID or birth certificate, and address proof",
            "Revenue officer verifies residency",
            "Issued within 7–15 working days"
        ],
        "methods": ["e-District Portal Online", "Tehsildar Office", "CSC Centre"]
    },
    "Marksheet": {
        "name": "Academic Marksheet / Certificate",
        "icon": "🎓",
        "url": "https://digilocker.gov.in",
        "steps": [
            "Log in to DigiLocker with your Aadhaar-linked mobile",
            "Search for your board or university under 'Issued Documents'",
            "Download the digitally signed marksheet instantly",
            "Use the digital version for all government scheme applications"
        ],
        "methods": ["DigiLocker (Instant Download)", "School/University Office", "Board Website"]
    },
    "EWS Certificate": {
        "name": "EWS (Economically Weaker Section) Certificate",
        "icon": "📋",
        "url": "https://serviceonline.gov.in",
        "steps": [
            "Apply through e-District portal or Tehsildar office",
            "Submit income proof (< ₹8 Lakh), Aadhaar, land records",
            "Revenue officer verifies income and assets",
            "Valid for one financial year; renew annually"
        ],
        "methods": ["e-District Portal Online", "Tehsildar / SDM Office", "CSC Centre"]
    },
    "SHG Registration": {
        "name": "Self Help Group (SHG) Registration",
        "icon": "👩‍👩‍👧‍👧",
        "url": "https://nrlm.gov.in",
        "steps": [
            "Form a group of 10–20 members (women-focused under DAY-NRLM)",
            "Register with your Block Development Office or DRDA",
            "Open a joint SHG bank account",
            "Get linked to NRLM for revolving fund and training support"
        ],
        "methods": ["Block Development Office", "DRDA / Zila Parishad", "NRLM Portal"]
    },
    "SHG Certificate": {
        "name": "Self Help Group Certificate",
        "icon": "👩‍👩‍👧‍👧",
        "url": "https://nrlm.gov.in",
        "steps": [
            "Ensure your SHG is registered with Block Development Office",
            "Request the SHG certificate from the Block coordinator",
            "Attach it to applications for NRLM, Drone Didi, or Mudra loans"
        ],
        "methods": ["Block Development Office", "NRLM Portal"]
    }
}


def detect_missing_documents(profile: Dict[str, Any], matched_schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify all unique required documents from matched schemes,
    and return actionable guidance for each."""
    all_required_docs = set()
    for scheme in matched_schemes:
        docs = scheme.get("documents", [])
        if isinstance(docs, list):
            for d in docs:
                all_required_docs.add(d.strip())

    # Add caste certificate if user is SC/ST/OBC
    caste = profile.get("caste", "General")
    if caste in ["SC/ST", "OBC"]:
        all_required_docs.add("Caste Certificate")

    # Add EWS cert if income < 8L and General caste
    if caste == "General" and profile.get("income", 0) > 0 and profile.get("income", 0) < 800000:
        all_required_docs.add("EWS Certificate")

    # Add domicile if state is specified
    if profile.get("state") and profile["state"] != "Unspecified":
        all_required_docs.add("Domicile Certificate")

    missing = []
    for doc_name in sorted(all_required_docs):
        guide = DOCUMENT_GUIDE.get(doc_name)
        if guide:
            missing.append({
                "document": guide["name"],
                "icon": guide["icon"],
                "url": guide["url"],
                "steps": guide["steps"],
                "methods": guide["methods"]
            })
        else:
            missing.append({
                "document": doc_name,
                "icon": "📄",
                "url": "https://serviceonline.gov.in",
                "steps": [f"Search for '{doc_name}' on your state's e-District or service portal.", "Submit required identity and address proofs.", "Collect via post or download online."],
                "methods": ["State e-District Portal", "Nearest Government Office"]
            })

    return missing


def analyze(text: str, income: float = 0, state: str = "", category: str = "", language: str = "en", caste: str = "") -> Dict[str, Any]:
    """
    Full analysis pipeline: validate → parse → match → detect conflicts → summarize.
    
    This is the main entry point for the API.
    Short-circuits with 0 matches if input is detected as invalid/absurd.
    
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
    from deep_translator import GoogleTranslator
    schemes = load_schemes()

    if language != "en" and text.strip():
        try:
            text = GoogleTranslator(source='auto', target='en').translate(text)
        except Exception as e:
            print(f"Translation Error: {e}")

    profile = parse_profile(text, income, state, category, caste)

    # ── Short-circuit on validation errors ──
    if profile.get("validationError"):
        return {
            "profile": profile,
            "schemes": [],
            "conflicts": [],
            "warnings": [profile["validationError"]],
            "improvements": [],
            "summary": profile["validationError"],
            "top5": [],
            "totalSchemesSearched": len(schemes),
            "matchCount": 0,
            "validationError": profile["validationError"]
        }

    matched, warnings, improvements = match_schemes(profile, schemes)

    # Add validation warnings from profile parsing
    for vw in profile.get("validationWarnings", []):
        warnings.append(vw)

    conflicts = detect_conflicts(matched)
    summary = generate_summary(profile, matched, language)
    
    if language != "en":
        from deep_translator import GoogleTranslator
        try:
            translator = GoogleTranslator(source='en', target=language)
            warnings = [translator.translate(w) if w else w for w in warnings]
            improvements = [translator.translate(imp) if imp else imp for imp in improvements]
        except Exception as e:
            print(f"Output translation error: {e}")
            
    top5 = rank_top_5_schemes(profile, matched)
    missing_docs = detect_missing_documents(profile, matched)

    return {
        "profile": profile,
        "schemes": matched,
        "conflicts": conflicts,
        "warnings": warnings,
        "improvements": improvements,
        "summary": summary,
        "top5": top5,
        "missingDocuments": missing_docs,
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
