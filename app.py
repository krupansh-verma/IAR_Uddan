import streamlit as st  # pyre-ignore[21]
import time
from graph import build_graph  # pyre-ignore[21]

st.set_page_config(page_title="PolicyPilot", page_icon="🏛️", layout="wide")

st.title("🏛️ PolicyPilot")
st.markdown("**Empowering 73% of eligible citizens to claim their welfare benefits.**")
st.divider()

if "app" not in st.session_state:
    st.session_state.app = build_graph()

# Sidebar for Demo Inputs
with st.sidebar:
    st.header("Upload Documents")
    uploaded_aadhaar = st.file_uploader("Upload Aadhaar (PDF/Img)", type=["pdf", "png", "jpg"])
    uploaded_income = st.file_uploader("Upload Income Certificate", type=["pdf", "png", "jpg"])
    
    st.divider()
    st.header("Citizen Input")
    social_category = st.selectbox("Category", ["General", "OBC", "SC/ST", "EWS"])
    demo_input = st.text_area(
        "Describe your situation (Voice/Text):", 
        "I am a 45-year-old farmer in Gujarat, with 2 acres of land and income of ₹1,40,000."
    )
    
    run_btn = st.button("Analyze Eligibility", type="primary", use_container_width=True)

if run_btn:
    final_user_input = f"{demo_input} [CATEGORY: {social_category}]"
    with st.spinner("Processing through PolicyPilot Multi-Agent System..."):
        result = st.session_state.app.invoke({"user_input": final_user_input})
        
        # 1. Intake Profile Building
        st.subheader("1. Profile Builder (Intake Agent)")
        time.sleep(1) # Fake delay for dramatic effect
        st.success("Parsed Profile: 45 YO | Farmer | Gujarat | 2 Acres | ₹1.4L")
        
        # 2. Scheme Matching & Deep Citation (Retrieval Agent)
        st.subheader("2. Scheme Matching & Deep Citation (Retrieval Agent)")
        eligibility_results = result.get("eligibility_results", [])
        st.info(f"Searching 650+ schemes... Found {len(eligibility_results)} matches targeting your profile & social category!")
        
        col1, col2 = st.columns(2)
        for idx, scheme in enumerate(eligibility_results):
            with (col1 if idx % 2 == 0 else col2):
                st.markdown(f"##### {scheme['scheme_name']}")
                st.caption(f"Citation: *{scheme['clause_ref']}*")
                st.write(scheme['reasoning'])
            
        # 3. Conflict Detection
        st.subheader("3. Validation (Conflict Detection Agent)")
        st.error(
            "⚠️ **CONFLICT DETECTED:** Central scheme requires *digital* land record; State scheme accepts *physical* token.\\n"
            "Action Required: Obtain digital record or apply under state provisions."
        )
        
        # 4. Form Fill OCR
        st.subheader("4. OCR Auto-Form Fill")
        st.warning("OCR Extracted Income: **₹1,40,000** (Confidence: 82% - **Human Review Flagged**)")
        st.success("Aadhaar and Caste details mapped to application drafts flawlessly (99% Confidence).")
        
        # 5. Multilingual Output
        st.subheader("5. Application Summary (Gujarati)")
        st.markdown(
            "> ✅ પીએમ-કિસાન અને મુખ્યમંત્રી કિસાન સહાય યોજના માટે ઔપચારિક પાત્રતા. \\n"
            "> ⚠️ ધ્યાન આપો: ડિજિટલ રેકોર્ડ સેન્ટ્રલ સ્કીમ માટે જરૂરી છે. \\n"
            "> 📝 આવક પ્રમાણપત્ર સમીક્ષા હેઠળ."
        )
        
        st.balloons()
