"""
YojnaAI — Flask API Server
Serves scheme data, runs eligibility analysis, and provides PDF registry.
"""

import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add project root to path so we can import from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eligibility import analyze, load_schemes, load_pdf_registry, load_conflict_rules

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True,
     allow_headers=["Content-Type", "X-Gemini-Key"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "YojnaAI Backend",
        "version": "1.0.0"
    })


@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    """
    GET /api/schemes
    Returns all scheme data from data/schemes.json.
    Optional query params: ?category=agriculture&scope=central
    """
    schemes = load_schemes()

    # Optional filtering
    category = request.args.get("category")
    scope = request.args.get("scope")

    if category:
        schemes = [s for s in schemes if s.get("category") == category]
    if scope:
        schemes = [s for s in schemes if s.get("scope") == scope]

    return jsonify({
        "total": len(schemes),
        "schemes": schemes
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_eligibility():
    """
    POST /api/analyze
    Accepts citizen profile, returns matching schemes + conflicts + summary.
    
    Request body (JSON):
    {
        "text": "I am a 45-year-old farmer with 2 acres",
        "income": 140000,
        "state": "Gujarat",
        "category": "agriculture",
        "language": "en"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    text = data.get("text", "")
    income = data.get("income", 0)
    state = data.get("state", "")
    category = data.get("category", "")
    caste = data.get("caste", "")
    language = data.get("language", "en")

    if not text and not income and not state:
        return jsonify({"error": "At least one of 'text', 'income', or 'state' is required"}), 400

    try:
        result = analyze(text, income, state, category, language, caste)
        return jsonify(result)
    except Exception as e:
        import traceback
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend_errors.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- ANALYSIS ERROR ---\n")
            f.write(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Gemini AI Chatbot endpoint powered by schemes.json context.
    Features Local Fallback for missing API keys and Strict Policy Guardrails.
    """
    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"error": "Message required"}), 400

    user_msg = data.get("message")
    
    try:
        schemes = load_schemes()
        
        # 1. API KEY CHECK & LOCAL FALLBACK
        api_key = (request.headers.get("X-Gemini-Key") or "").strip()
        if not api_key:
            api_key = (os.environ.get("GEMINI_API_KEY") or "").strip()
        
        if not api_key:
            lower = user_msg.lower()
            if any(greeting in lower for greeting in ["hello", "hi", "hy", "hey", "नमस्ते"]):
                return jsonify({"reply": "Hello! I am the YojnaAI Assistant. Please ask about a policy (e.g., 'farming', 'student', or 'business') and I will help you."})
            
            # Smart Offline Keyword Matcher (Tokenization & Synonym Scoring)
            tokens = lower.split()
            
            synonyms = {
                "student": ["education", "scholarship", "css", "vidyalaxmi", "university", "college", "school"],
                "farm": ["agriculture", "kisan", "pmfby", "soil", "crop"],
                "farmer": ["agriculture", "kisan", "pmfby", "soil", "crop"],
                "business": ["startup", "mudra", "msme", "loan", "enterprise", "company"],
                "women": ["matru", "sukanya", "mahila", "lady", "girl"],
                "health": ["ayushman", "jay", "hospital", "medical", "healthcare", "treatment", "doctor"],
                "house": ["pmay", "housing", "awas", "home", "shelter"],
                "revenue": ["income", "tax", "ews", "finance", "subsidy", "grt", "money"],
                "immigration": ["nri", "visa", "overseas", "abroad", "pravasi", "immigrant", "worker"],
                "caste": ["sc", "st", "obc", "reservation", "minority", "tribe"],
                "pension": ["elderly", "senior", "old", "retire", "vridha"],
                "disability": ["handicap", "divyang", "pwd", "differently"],
                "food": ["ration", "pds", "annapurna", "grain", "wheat", "rice"],
                "land": ["plot", "acre", "hectare", "property", "bhumi"]
            }
            
            search_terms = set(tokens)
            for token in tokens:
                for syn, mapped_terms in synonyms.items():
                    if syn in token:
                        search_terms.update(mapped_terms)
                        
            best_schemes = []
            
            for s in schemes:
                score = 0
                s_title = s.get("title", "").lower()
                s_cat = s.get("category", "").lower()
                s_sum = s.get("summary", "").lower()
                
                for term in search_terms:
                    if len(term) < 3: continue
                    if term in s_title: score += 3
                    if term in s_cat: score += 2
                    if term in s_sum: score += 1
                    
                if score > 0:
                    best_schemes.append((score, s))
            
            best_schemes.sort(key=lambda x: x[0], reverse=True)
            top = best_schemes[:3]
                    
            if top:
                reply_parts = []
                for i, (sc, scheme) in enumerate(top, 1):
                    reply_parts.append(f"{i}. **{scheme.get('title', 'Policy')}**\n{scheme.get('summary', '')}\nLink: {scheme.get('url', 'N/A')}")
                return jsonify({"reply": "\n\n".join(reply_parts)})
            else:
                return jsonify({"reply": "I couldn't find an exact matching policy for that. Try keywords like 'farmer', 'student', 'business', 'housing', 'healthcare', 'pension', or 'food'."})

        # 2. GEMINI AI EXECUTION
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        context = json.dumps(schemes[:50], ensure_ascii=False)
        
        # 3. STRICT POLICY OPTIMIZATION
        system_instruction = (
            "You are the YojnaAI AI assistant. STRICT REGULATION: You must ONLY answer questions related to Indian government schemes, welfare, and policies. "
            "If the user asks a general question (e.g., 'hi', 'how are you', 'what is the weather', 'who won the match', math equations, etc.), you MUST completely decline answering and say exactly: "
            "'I am the YojnaAI Assistant. I am strictly programmed to assist you only with Indian Government Policies and Welfare Schemes. How can I help you with policies today?' "
            f"If it is a valid policy query, use the following Indian government schemes context exclusively to answer: {context}. Speak directly, concisely, and professionally without hallucinating."
        )
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_msg)
        return jsonify({"reply": response.text})
        
    except Exception as e:
        import traceback
        err_str = str(e).lower()
        
        # Catch invalid API key errors gracefully
        if "api key not valid" in err_str or "api_key_invalid" in err_str or "invalid" in err_str:
            return jsonify({"reply": "⚠️ Your Gemini API Key is invalid. Please click ⚙️ Settings and paste a valid key from https://aistudio.google.com/app/apikey"})
        
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend_errors.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- CHAT GENERATION ERROR ---\n")
            f.write(traceback.format_exc())
        return jsonify({"reply": f"AI Generation Error: {str(e)}"})


@app.route("/api/pdf-registry", methods=["GET"])
def get_pdf_registry():
    """
    GET /api/pdf-registry
    Returns metadata for all official PDF source documents.
    """
    registry = load_pdf_registry()
    return jsonify({
        "total": len(registry),
        "pdfSources": registry
    })


@app.route("/api/conflicts", methods=["GET"])
def get_conflict_rules():
    """
    GET /api/conflicts
    Returns all conflict detection rules.
    """
    rules = load_conflict_rules()
    return jsonify({
        "total": len(rules),
        "conflictRules": rules
    })


if __name__ == "__main__":
    print("=" * 50)
    print("YojnaAI Backend API Server")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print("Endpoints:")
    print("  GET  /api/health        — Health check")
    print("  GET  /api/schemes       — All schemes (?category=&scope=)")
    print("  POST /api/analyze       — Run eligibility analysis")
    print("  GET  /api/pdf-registry  — PDF source metadata")
    print("  GET  /api/conflicts     — Conflict detection rules")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=True)
