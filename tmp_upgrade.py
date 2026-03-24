import re
import os

filepath = os.path.join("frontend", "standalone_react.html")
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace the TRANSLATIONS dict completely
new_translations = """const TRANSLATIONS = {
      en: {
        titleSub: "AI Welfare Claims Eligibility System", intakeBadge: "Data Intake", intakeLabel: "Input Citizen Metrics",
        analyzeBtn: "Analyze Eligibility", processing: "Processing...", successTitle: "Profile Verified", warningTitle: "Profile Alerts",
        matchesBadge: "Policy Match", matchesTitle: "Eligible Schemes Found", noMatches: "No active schemes match your current profile.", 
        dashAnnualIncome: "💰 Annual Income (₹)", dashState: "📍 State", dashCategory: "🏷️ Need Category",
        summaryTitle: "PolicyPilot Analysis", logoutBtn: "Logout",
        tagAge: "Age: ", tagState: "State: ", tagIncome: "Income: ", tagNone: "None",
        authHeading1: "Policy", authHeading2: "Pilot",
        botGreeting: "Namaste! How can I help you today?", botFallback: "I'm looking for relevant policies. Try asking about 'farming', 'students', or 'pension'.", botError: "I encountered an error understanding your query."
      },
      hi: {
        titleSub: "AI कल्याण दावा प्रणाली", intakeBadge: "डेटा इनटेक", intakeLabel: "विवरण दर्ज करें",
        analyzeBtn: "पात्रता विश्लेषण", processing: "प्रोसेसिंग...", successTitle: "प्रोफ़ाइल सत्यापित", warningTitle: "अलर्ट",
        matchesBadge: "योजना मिलान", matchesTitle: "पात्र योजनाएं", noMatches: "कोई योजना मेल नहीं खाती।",
        dashAnnualIncome: "💰 वार्षिक आय (₹)", dashState: "📍 राज्य", dashCategory: "🏷️ श्रेणी",
        summaryTitle: "पॉलिसीपायलट विश्लेषण", logoutBtn: "लॉग आउट",
        tagAge: "आयु: ", tagState: "राज्य: ", tagIncome: "आय: ", tagNone: "कोई नहीं",
        authHeading1: "पॉलिसी", authHeading2: "पायलट",
        botGreeting: "नमस्ते! मैं आज आपकी कैसे मदद कर सकता हूँ?", botFallback: "मैं प्रासंगिक नीतियों की तलाश कर रहा हूं। 'खेती', 'छात्रों', या 'पेंशन' के बारे में पूछने का प्रयास करें।", botError: "मुझे आपकी क्वेरी समझने में त्रुटि हुई।"
      },
      gu: { 
        titleSub: "AI કલ્યાણ દાવો સિસ્ટમ", intakeBadge: "ડેટા ઇન્ટેક", intakeLabel: "વિગતો દાખલ કરો",
        analyzeBtn: "પાત્રતા વિશ્લેષણ", processing: "પ્રક્રિયા થઈ રહી છે...", successTitle: "પ્રોફાઇલ ચકાસાયેલ", warningTitle: "ચેતવણીઓ",
        matchesBadge: "યોજના મેચ", matchesTitle: "પાત્ર યોજનાઓ", noMatches: "કોઈ યોજના મેળ ખાતી નથી.",
        dashAnnualIncome: "💰 વાર્ષિક આવક (₹)", dashState: "📍 રાજ્ય", dashCategory: "🏷️ શ્રેણી",
        summaryTitle: "પોલિસીપાયલટ વિશ્લેષણ", logoutBtn: "લૉગ આઉટ",
        tagAge: "ઉંમર: ", tagState: "રાજ્ય: ", tagIncome: "આવક: ", tagNone: "કોઈ નહિ",
        authHeading1: "પોલિસી", authHeading2: "પાયલટ",
        botGreeting: "નમસ્તે! હું આજે તમારી કેવી રીતે મદદ કરી શકું?", botFallback: "હું સંબંધિત નીતિઓ શોધી રહ્યો છું. 'ખેતી', 'વિદ્યાર્થીઓ' અથવા 'પેન્શન' વિશે પૂછવાનો પ્રયાસ કરો.", botError: "ભૂલ આવી છે."
      },
      mr: {
        titleSub: "AI कल्याण दावा प्रणाली", intakeBadge: "डेटा इनटेक", intakeLabel: "तपशील प्रविष्ट करा",
        analyzeBtn: "पात्रता विश्लेषण", processing: "प्रक्रिया करत आहे...", successTitle: "प्रोफाइल सत्यापित", warningTitle: "सूचना",
        matchesBadge: "योजना जुळणी", matchesTitle: "पात्र योजना", noMatches: "कोणतीही योजना जुळत नाही.",
        dashAnnualIncome: "💰 वार्षिक उत्पन्न (₹)", dashState: "📍 राज्य", dashCategory: "🏷️ श्रेणी",
        summaryTitle: "पॉलिसीपायलट विश्लेषण", logoutBtn: "लॉग आउट",
        tagAge: "वय: ", tagState: "राज्य: ", tagIncome: "उत्पन्न: ", tagNone: "काहीही नाही",
        authHeading1: "पॉलिसी", authHeading2: "पायलट",
        botGreeting: "नमस्कार! मी आज तुमची कशी मदत करू शकेन?", botFallback: "मी संबंधित धोरणे शोधत आहे. 'शेती', 'विद्यार्थी' किंवा 'पेन्शन' बद्दल विचारून पहा.", botError: "मला समजण्यास त्रुटी आली."
      },
      ta: {
        titleSub: "AI நல உரிமை கோரல் அமைப்பு", intakeBadge: "தரவு உள்ளீடு", intakeLabel: "விவரங்களை உள்ளிடவும்",
        analyzeBtn: "தகுதி பகுப்பாய்வு", processing: "செயலாக்கப்படுகிறது...", successTitle: "சுயவிவரம் சரிபார்க்கப்பட்டது", warningTitle: "எச்சரிக்கைகள்",
        matchesBadge: "திட்டப் பொருத்தம்", matchesTitle: "தகுதியான திட்டங்கள்", noMatches: "எந்த திட்டமும் பொருந்தவில்லை.",
        dashAnnualIncome: "💰 ஆண்டு வருமானம் (₹)", dashState: "📍 மாநிலம்", dashCategory: "🏷️ வகை",
        summaryTitle: "பாலிசிபைலட் பகுப்பாய்வு", logoutBtn: "வெளியேறு",
        tagAge: "வயது: ", tagState: "மாநிலம்: ", tagIncome: "வருமானம்: ", tagNone: "ஏதுமில்லை",
        authHeading1: "பாலிசி", authHeading2: "பைலட்",
        botGreeting: "வணக்கம்! இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?", botFallback: "நான் கொள்கைகளைத் தேடுகிறேன். 'விவசாயம்' பற்றி கேட்கவும்.", botError: "பிழை ஏற்பட்டது."
      },
      te: {
        titleSub: "AI సంక్షేమ దావా వ్యవస్థ", intakeBadge: "డేటా ఇన్‌టేక్", intakeLabel: "వివరాలను నమోదు చేయండి",
        analyzeBtn: "అర్హత విశ్లేషణ", processing: "ప్రాసెస్ చేయబడుతోంది...", successTitle: "ప్రొఫైల్ ధృవీకరించబడింది", warningTitle: "హెచ్చరికలు",
        matchesBadge: "పథకం సరిపోలిక", matchesTitle: "అర్హత ఉన్న పథకాలు", noMatches: "ఏ పథకం సరిపోలడం లేదు.",
        dashAnnualIncome: "💰 వార్షిక ఆదాయం (₹)", dashState: "📍 రాష్ట్రం", dashCategory: "🏷️ వర్గం",
        summaryTitle: "పాలసీపైలట్ విశ్లేషణ", logoutBtn: "లాగ్ అవుట్",
        tagAge: "వయస్సు: ", tagState: "రాష్ట్రం: ", tagIncome: "ఆదాయం: ", tagNone: "ఏమీ లేదు",
        authHeading1: "పాలసీ", authHeading2: "పైలట్",
        botGreeting: "నమస్తే! నేను ఎలా సహాయపడగలను?", botFallback: "నేను విధానాల కోసం చూస్తున్నాను. 'వ్యవసాయం' గురించి అడగండి.", botError: "లోపం ఏర్పడింది."
      },
      pa: {
        titleSub: "AI ਭਲਾਈ ਦਾਅਵਾ ਪ੍ਰਣਾਲੀ", intakeBadge: "ਡੇਟਾ ਇਨਟੇਕ", intakeLabel: "ਵੇਰਵੇ ਦਰਜ ਕਰੋ",
        analyzeBtn: "ਯੋਗਤਾ ਵਿਸ਼ਲੇਸ਼ਣ", processing: "ਕਾਰਵਾਈ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ...", successTitle: "ਪ੍ਰੋਫਾਈਲ ਪ੍ਰਮਾਣਿਤ", warningTitle: "ਚੇਤਾਵਨੀਆਂ",
        matchesBadge: "ਸਕੀਮ ਮੇਲ", matchesTitle: "ਯੋਗ ਸਕੀਮਾਂ", noMatches: "ਕੋਈ ਸਕੀਮ ਮੇਲ ਨਹੀਂ ਖਾਂਦੀ।",
        dashAnnualIncome: "💰 ਸਾਲਾਨਾ ਆਮਦਨ (₹)", dashState: "📍 ਰਾਜ", dashCategory: "🏷️ ਸ਼੍ਰੇਣੀ",
        summaryTitle: "ਪਾਲਿਸੀਪਾਇਲਟ ਵਿਸ਼ਲੇਸ਼ਣ", logoutBtn: "ਲੌਗ ਆਉਟ",
        tagAge: "ਉਮਰ: ", tagState: "ਰਾਜ: ", tagIncome: "ਆਮਦਨ: ", tagNone: "ਕੁਝ ਨਹੀਂ",
        authHeading1: "ਪਾਲਿਸੀ", authHeading2: "ਪਾਇਲਟ",
        botGreeting: "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਅੱਜ ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?", botFallback: "ਮੈਂ ਨੀਤੀਆਂ ਲੱਭ ਰਿਹਾ ਹਾਂ। 'ਖੇਤੀ' ਬਾਰੇ ਪੁੱਛੋ।", botError: "ਗਲਤੀ ਆਈ ਹੈ।"
      },
      bn: {
        titleSub: "AI কল্যাণ দাবি সিস্টেম", intakeBadge: "ডেটা ইনটেক", intakeLabel: "বিবরণ লিখুন",
        analyzeBtn: "যোগ্যতা বিশ্লেষণ", processing: "প্রক্রিয়া চলছে...", successTitle: "প্রোফাইল যাচাইকৃত", warningTitle: "সতর্কতা",
        matchesBadge: "স্কিম মিল", matchesTitle: "যোগ্য স্কিম", noMatches: "কোন স্কিম মিলে না।",
        dashAnnualIncome: "💰 বার্ষিক আয় (₹)", dashState: "📍 রাজ্য", dashCategory: "🏷️ বিভাগ",
        summaryTitle: "পলিসিপাইলট বিশ্লেষণ", logoutBtn: "লগ আউট",
        tagAge: "বয়স: ", tagState: "রাজ্য: ", tagIncome: "আয়: ", tagNone: "কিছুই না",
        authHeading1: "পলিসি", authHeading2: "পাইলট",
        botGreeting: "নমস্কার! আমি কীভাবে সাহায্য করতে পারি?", botFallback: "আমি নীতি খুঁজছি। 'কৃষি' সম্পর্কে জিজ্ঞাসা করুন।", botError: "একটি ত্রুটি ঘটেছে।"
      }
    };"""

content = re.sub(r"const TRANSLATIONS = \{[\s\S]*?\n    };\n", new_translations + "\n", content)

# 2. Replace Chatbot component
new_chatbot = """const Chatbot = ({ schemes, language, t }) => {
      const [isOpen, setIsOpen] = useState(false);
      const [messages, setMessages] = useState([{ sender: 'bot', text: t?.botGreeting || 'Namaste! How can I help you today?' }]);
      const [input, setInput] = useState('');
      const endRef = useRef(null);

      useEffect(() => {
        if (messages.length <= 1) {
            setMessages([{ sender: 'bot', text: t?.botGreeting || 'Namaste! How can I help you today?' }]);
        }
      }, [language, t]);

      useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

      const handleSend = () => {
        if (!input.trim()) return;
        const msg = input.trim();
        setMessages(prev => [...prev, { sender: 'user', text: msg }]);
        setInput('');
        setTimeout(() => {
          try {
            const lower = msg.toLowerCase();
            const s = (schemes||[]).find(x => 
              (x.title && lower.includes(x.title.toLowerCase())) || 
              (x.category && lower.includes(x.category.toLowerCase())) ||
              (x.translations && x.translations[language] && lower.includes(x.translations[language].split(":")[0].toLowerCase()))
            );
            
            let res = t?.botFallback || "I'm looking for relevant policies. Try asking about farming, students, or pensions.";
            if (s) {
               const schemeTitle = (s.translations && s.translations[language]) ? s.translations[language].split(':')[0] : s.title;
               const schemeSummary = s.summary; 
               res = `${schemeTitle}: ${schemeSummary}\\n\\nLink: ${s.url}`;
            }
            // Smart reply logic for basic keywords
            if (lower.includes("hello") || lower.includes("hi") || lower.includes("नमस्ते")) {
                res = t?.botGreeting || "Hello! State your situation (e.g. 'farmer from UP') and I'll find policies.";
            }
            setMessages(prev => [...prev, { sender: 'bot', text: res }]);
          } catch(e) {
            console.error("Chatbot Error:", e);
            setMessages(prev => [...prev, { sender: 'bot', text: t?.botError || "Error understanding query." }]);
          }
        }, 600);
      };

      return (
        <>
          {isOpen && (
            <div className="chatbot-window">
              <div className="chatbot-header"><h4>Assistant</h4><button onClick={() => setIsOpen(false)} style={{background:'transparent',border:'none',color:'white',fontSize:'1.2rem',cursor:'pointer'}}>✕</button></div>
              <div className="chatbot-messages">
                {messages.map((m, i) => <div key={i} className={`chat-msg ${m.sender}`}>{m.text}</div>)}
                <div ref={endRef} />
              </div>
              <div className="chatbot-input">
                <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()} placeholder="Type here..." />
                <button onClick={handleSend}>Send</button>
              </div>
            </div>
          )}
          <button className="chatbot-fab" onClick={() => setIsOpen(true)}>🤖</button>
        </>
      );
    };"""

content = re.sub(r"const Chatbot = \(\{ schemes \}\) => \{[\s\S]*?    \};\n", new_chatbot + "\n", content)

# 3. Update Dashboard to pass t and language to Chatbot
content = content.replace("<Chatbot schemes={initialSchemes} />", "<Chatbot schemes={initialSchemes} language={language} t={t} />")

# 4. Update Languages Selector
new_selector = """<select className="lang-selector" onChange={e => setLanguage(e.target.value)} value={language}>
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="gu">ગુજરાતી</option>
              <option value="mr">मराठी</option>
              <option value="ta">தமிழ்</option>
              <option value="te">తెలుగు</option>
              <option value="pa">ਪੰਜਾਬੀ</option>
              <option value="bn">বাংলা</option>
            </select>"""
content = re.sub(r'<select className="lang-selector"[\s\S]*?</select>', new_selector, content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully overhauled {filepath} with multilingual support and robust chatbot.")
