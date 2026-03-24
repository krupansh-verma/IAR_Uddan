import React, { useState } from 'react';

function App() {
  const [inputText, setInputText] = useState("I am a 45-year-old farmer in Gujarat, with 2 acres of land and income of ₹1,40,000.");
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultsConfig, setResultsConfig] = useState(null);

  const handleAnalyze = () => {
    setIsProcessing(true);
    setResultsConfig(null);
    
    // Simulate backend LangGraph processing time
    setTimeout(() => {
      setIsProcessing(false);
      setResultsConfig(true);
    }, 2000);
  };

  return (
    <div className="container">
      <header>
        <h1>🏛️ PolicyPilot</h1>
        <p>Empowering 73% of eligible citizens to claim their welfare benefits.</p>
      </header>

      <main>
        <div className="glass-panel">
          <div className="input-group">
            <label htmlFor="citizen-input">Describe your situation (Voice/Text):</label>
            <textarea 
              id="citizen-input"
              rows="4" 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </div>
          <button 
            className="btn-primary" 
            onClick={handleAnalyze} 
            disabled={isProcessing}
          >
            {isProcessing ? "Processing via Multi-Agent System..." : "Analyze Eligibility"}
          </button>
        </div>

        {isProcessing && <div className="spinner"></div>}

        {resultsConfig && (
          <div className="results-container">
            {/* Step 1: Intake */}
            <div className="status-card status-success" style={{ animationDelay: '0.1s' }}>
              <h3>✓ 1. Profile Builder (Intake Agent)</h3>
              <p><strong>Parsed Profile:</strong> 45 YO | Farmer | Gujarat | 2 Acres | ₹1.4L</p>
            </div>

            {/* Step 2: Retrieval */}
            <div className="glass-panel" style={{ animation: 'slideIn 0.5s ease-out forwards', animationDelay: '0.3s', opacity: 0 }}>
              <h3 style={{ marginBottom: '1rem', color: 'var(--primary)' }}>2. Scheme Matching & Deep Citation (Retrieval Agent)</h3>
              <p>Searching 650+ schemes... Found 2 matches!</p>
              
              <div className="grid-2">
                <div className="scheme-card">
                  <h4>🌾 PM-Kisan (Central)</h4>
                  <span className="citation">Citation: Section 3, Clause B</span>
                  <p>Requires digital land record showing ownership up to 2 hectares to receive ₹6,000.</p>
                </div>
                <div className="scheme-card">
                  <h4>🌾 Mukhyamantri Kisan Sahay Yojana (State)</h4>
                  <span className="citation">Citation: Section 1, Clause 4</span>
                  <p>Holding up to 2 hectares eligible. Physical token acceptable in lieu of digital.</p>
                </div>
              </div>
            </div>

            {/* Step 3: Conflict */}
            <div className="status-card status-danger" style={{ animationDelay: '0.5s' }}>
              <h3>⚠️ 3. Validation (Conflict Detection Agent)</h3>
              <p><strong>CONFLICT DETECTED:</strong> Central scheme requires <em>digital</em> land record; State scheme accepts <em>physical</em> token.</p>
              <p style={{marginTop: '0.5rem', fontSize: '0.9rem'}}><strong>Action Required:</strong> Obtain digital record or apply under state provisions.</p>
            </div>

            {/* Step 4: Form Fill OCR */}
            <div className="status-card status-warning" style={{ animationDelay: '0.7s' }}>
              <h3>📝 4. OCR Auto-Form Fill</h3>
              <p><strong>OCR Extracted Income:</strong> ₹1,40,000 (Confidence: 82% - <strong>Human Review Flagged</strong>)</p>
              <p style={{marginTop: '0.5rem'}}>Aadhaar details mapped to application drafts flawlessly (99% Confidence).</p>
            </div>

            {/* Step 5: Output */}
            <div className="glass-panel" style={{ animation: 'slideIn 0.5s ease-out forwards', animationDelay: '0.9s', opacity: 0 }}>
              <h3 style={{ marginBottom: '1rem', color: 'var(--success)' }}>🌐 5. Application Summary (Gujarati)</h3>
              <div style={{ padding: '1rem', background: '#f8fafc', borderRadius: '8px', borderLeft: '4px solid var(--primary)' }}>
                <p>✅ પીએમ-કિસાન અને મુખ્યમંત્રી કિસાન સહાય યોજના માટે ઔપચારિક પાત્રતા.</p>
                <p>⚠️ ધ્યાન આપો: ડિજિટલ રેકોર્ડ સેન્ટ્રલ સ્કીમ માટે જરૂરી છે.</p>
                <p>📝 આવક પ્રમાણપત્ર સમીક્ષા હેઠળ.</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
