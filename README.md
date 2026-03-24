# YojnaAI (PolicyPilot) 🇮🇳

YojnaAI is an advanced, AI-powered government policy recommendation engine designed to intelligently match Indian citizens with the welfare schemes they are eligible for. By leveraging a structured data layer, a comprehensive RAG (Retrieval-Augmented Generation) architecture, and localized UI components, YojnaAI makes discovering government benefits seamless, accessible, and highly personalized.

## 🌟 Key Features
- **Smart Eligibility Engine**: Filters policies based on age, income, state, occupation, category, and caste ensuring citizens only see schemes they qualify for.
- **AI-Powered Recommendations**: Ranks schemes using a custom heuristic algorithm weighing Eligibility Match, Need Relevance, Benefit Value, and Priority Level (with diversity constraints so users see varied domains like Health, Education, Farming).
- **RAG Architecture**: Ingests actual scheme guidances and legal clauses (e.g., PM-Kisan, Vidyalaxmi, PMAY) to provide exact PDF origins, page numbers, and strict eligibility rule verifications.
- **Multilingual Support**: Supports English, Hindi, Gujarati, Marathi, Tamil, Telugu, Punjabi, and Bengali to cater to users across the subcontinent.
- **Conflict Detection Agent**: Automatically detects and alerts users to policy contradictions between Central and State-level schemes.
- **Indian National Aesthetic**: Designed with a cinematic, artistic User Interface utilizing the Indian tricolors (Deep Saffron, White, Indian Green) seamlessly merged with modern UI/UX design components.

## 🛠️ Technology Stack
- **Frontend**: Standalone React environment (`standalone_react.html`) configured for zero-build-step deployment, coupled with responsive vanilla CSS ensuring an artistic, lightweight interface.
- **Backend API**: Python-based Flask server (`backend/server.py`) handling all REST endpoints and JSON processing.
- **Eligibility Engine**: Core logic parser (`backend/eligibility.py`) handling complex dict-matching, score calculations, and priority enforcement mapping.
- **Agentic AI**: Built utilizing `langgraph` framework with defined State Graphs (Intake Node, Retrieval Node, Eligibility Node, Form-Fill Node) mapping directly to the LLM (Gemini).

## 🚀 Running the Project

### 1. Start the Backend API
The Python backend must be running to process eligibility analysis.
```bash
# From the project root, simply run:
py run_server.py
```
*The server will start on `http://localhost:5001`. Keep the terminal open.*

### 2. Launch the Web Interface
Double-click and open the following file directly in your web browser:
```text
frontend/standalone_react.html
```
*You can now select languages, use the microphone input, and analyze profiles live!*

---
**Built to empower the citizens of India.** 🇮🇳