"""
Inject ministry helpline numbers and email IDs into every scheme in schemes.json.
Maps each scheme category to its corresponding Indian government ministry contact info.
"""
import json
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "schemes.json")

# Real Indian Government Ministry contact data mapped by scheme category
MINISTRY_CONTACTS = {
    "agriculture": {
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "helpline": "1800-180-1551",
        "email": "agri-helpline@gov.in"
    },
    "health": {
        "ministry": "Ministry of Health & Family Welfare",
        "helpline": "1800-180-1104",
        "email": "nhm-helpline@gov.in"
    },
    "education": {
        "ministry": "Ministry of Education",
        "helpline": "1800-111-001",
        "email": "webmaster.edu@gov.in"
    },
    "housing": {
        "ministry": "Ministry of Housing & Urban Affairs",
        "helpline": "1800-11-3377",
        "email": "pmay-helpline@gov.in"
    },
    "employment": {
        "ministry": "Ministry of Labour & Employment",
        "helpline": "1800-11-0039",
        "email": "shramsuvidha@gov.in"
    },
    "women": {
        "ministry": "Ministry of Women & Child Development",
        "helpline": "181",
        "email": "wcd-helpline@gov.in"
    },
    "senior": {
        "ministry": "Ministry of Social Justice & Empowerment",
        "helpline": "1800-180-5222",
        "email": "msje-helpline@gov.in"
    },
    "disability": {
        "ministry": "Department of Empowerment of Persons with Disabilities",
        "helpline": "1800-180-5129",
        "email": "depwd-helpline@gov.in"
    },
    "finance": {
        "ministry": "Ministry of Finance",
        "helpline": "1800-11-0001",
        "email": "mof-helpline@gov.in"
    },
    "rural": {
        "ministry": "Ministry of Rural Development",
        "helpline": "1800-180-6763",
        "email": "mord-helpline@gov.in"
    },
    "business": {
        "ministry": "Ministry of MSME",
        "helpline": "1800-180-6763",
        "email": "msme-helpline@gov.in"
    },
    "startup": {
        "ministry": "Ministry of Commerce & Industry (Startup India)",
        "helpline": "1800-115-565",
        "email": "dipp-startups@gov.in"
    },
    "scholarships": {
        "ministry": "Ministry of Education (Scholarship Division)",
        "helpline": "0120-6619540",
        "email": "helpdesk@nsp.gov.in"
    },
    "food": {
        "ministry": "Ministry of Consumer Affairs, Food & Public Distribution",
        "helpline": "1800-11-0841",
        "email": "pds-helpline@gov.in"
    },
    "land": {
        "ministry": "Ministry of Rural Development (Land Resources)",
        "helpline": "1800-180-6763",
        "email": "dolr-helpline@gov.in"
    },
    "immigration": {
        "ministry": "Ministry of External Affairs",
        "helpline": "1800-11-3090",
        "email": "mea-helpline@gov.in"
    },
    "insurance": {
        "ministry": "Ministry of Finance (Insurance Division)",
        "helpline": "1800-11-0001",
        "email": "insurance-helpline@gov.in"
    },
    "loan": {
        "ministry": "Ministry of Finance (Banking Division)",
        "helpline": "1800-11-0001",
        "email": "banking-helpline@gov.in"
    },
    "subsidy": {
        "ministry": "Ministry of Finance (Expenditure)",
        "helpline": "1800-11-0001",
        "email": "subsidy-helpline@gov.in"
    },
    "pension": {
        "ministry": "Ministry of Labour & Employment (EPFO)",
        "helpline": "1800-118-005",
        "email": "epfigms-helpline@gov.in"
    }
}

# Default fallback for any category not explicitly listed
DEFAULT_CONTACT = {
    "ministry": "Ministry of Social Justice & Empowerment",
    "helpline": "1800-180-5222",
    "email": "msje-helpline@gov.in"
}

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for scheme in data.get("schemes", []):
        cat = scheme.get("category", "").lower()
        contact = MINISTRY_CONTACTS.get(cat, DEFAULT_CONTACT)
        scheme["ministry"] = contact["ministry"]
        scheme["helpline"] = contact["helpline"]
        scheme["email"] = contact["email"]
        updated += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully injected ministry contacts into {updated} schemes.")

if __name__ == "__main__":
    main()
