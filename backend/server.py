"""
YojnaAI — Flask API Server
Serves scheme data, runs eligibility analysis, and provides PDF registry.
"""

import json
import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add project root to path so we can import from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eligibility import analyze, load_schemes, load_pdf_registry, load_conflict_rules

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
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
            if any(w in lower for w in ["how", "use", "help", "guide", "what", "eligibility", "check", "scan"]):
                return jsonify({"reply": "To find your eligibility: fill out your details (Age, Income, State, Need Category, Caste) on the dashboard and click the 'Analyze Eligibility' button."})
            elif any(w in lower for w in ["mic", "voice", "speak", "audio"]):
                return jsonify({"reply": "Click the Microphone (🎙) icon next to the text box. Speak your age, income, and needs in your selected language, and release the button to analyze."})
            elif any(w in lower for w in ["language", "translate", "hindi", "gujarati", "marathi", "bengali"]):
                return jsonify({"reply": "Use the language dropdown at the top of the screen to switch the whole site into your preferred language."})
            elif any(greeting in lower for greeting in ["hello", "hi", "hy", "hey", "नमस्ते"]):
                return jsonify({"reply": "Hello! I am the YojanaAI Navigator. Try asking 'How do I check my eligibility?' or 'How do I use the microphone?'"})
            else:
                return jsonify({"reply": "I am the offline Site Navigator. Please ask me how to use this website (e.g., 'help', 'microphone', 'eligibility'). (Note: To use the advanced Navigation AI, please add a Gemini API Key in Settings)."})
                
        # GEMINI AI EXECUTION
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        system_instruction = (
            "You are the YojanaAI Navigator, a website support assistant. Your SOLE purpose is to help citizens understand how to use this website to find welfare schemes. "
            "You MUST NOT suggest or explain specific Indian government policies or welfare schemes directly. "
            "Instead, instruct users on how to use the website's features: "
            "1. To find policies, tell them to fill out their details (Age, Income, State, Need Category, Caste) and click the 'Analyze Eligibility' button.\n"
            "2. To type or speak in their local language, tell them they can use the language dropdown at the top, and click the Microphone icon.\n"
            "3. To read policy details, tell them to click on any scheme card after analysis.\n"
            "If a user asks about a specific scheme (e.g., 'What is PM Kisan?'), decline politely and say: 'Please type your details in the main text box and click Analyze Eligibility to automatically match that scheme.' "
            "Keep your answers extremely concise, friendly, and strictly about website navigation."
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


# --- Static File Serving (for deployment) ---
@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'standalone_react.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), filename)

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(FRONTEND_DIR, 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(FRONTEND_DIR, 'sw.js')


if __name__ == "__main__":
    print("=" * 50)
    print("YojanaAI Backend API Server")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print("Serving frontend from:", FRONTEND_DIR)
    print("Endpoints:")
    print("  GET  /               — Frontend UI")
    print("  GET  /api/health     — Health check")
    print("  GET  /api/schemes    — All schemes")
    print("  POST /api/analyze    — Run eligibility analysis")
    print("  POST /api/chat       — Chatbot")
    print("=" * 50)
    port = int(os.environ.get('PORT', 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
