#!/usr/bin/env python3
import json, os

def S(id,title,emoji,scope,cat,cls,pdf,docId,clauseRef,pageRef,text,summary,url,deadline,elig,steps,docs,offices,rules,hi=""):
    return {"id":id,"title":title,"emoji":emoji,"scope":scope,"category":cat,"classification":cls,
        "pdfSource":pdf,"docId":docId,"clauseRef":clauseRef,"pageRef":pageRef,"extractedText":text,
        "summary":summary,"url":url,"deadline":deadline,
        "eligibility":elig,"steps":steps,"documents":docs,"offices":offices,"matchRules":rules,
        "translations":{"hi":hi} if hi else {}}

schemes = [
    # === AGRICULTURE (10) ===
    S("pm-kisan","PM-Kisan","🌾","central","agriculture","Central Sector","PM-KISAN_Guidelines.pdf","AGR-01","Clause 3","P7","...","₹6,000/year for farmers.","https://pmkisan.gov.in/","Mar 2026",
      [{"criterion":"Land ≤ 2 hectares"}],["Register online"],["Aadhaar","Land Record"],["CSC"],{"requiresFarmer":True,"maxAcres":2},"पीएम-किसान"),
    S("kcc","Kisan Credit Card","💳","central","agriculture","Credit","KCC_Guidelines.pdf","AGR-02","Sec 4","P6","...","Credit at 4% interest.","https://pmkisan.gov.in/","Year-round",
      [{"criterion":"All farmers eligible"}],["Apply at bank"],["Aadhaar","Land papers"],["Banks"],{"requiresFarmer":True}),
    S("pmfby","PM Fasal Bima","🌾","central","agriculture","Insurance","PMFBY_Guidelines.pdf","AGR-03","Sec 3","P5","...","Crop insurance at 2% premium.","https://pmfby.gov.in/","Sowing season",
      [{"criterion":"All farmers growing notified crops"}],["Apply online/bank"],["Aadhaar","Land Record"],["Banks"],{"requiresFarmer":True}),
    S("soil-health","Soil Health Card","🌱","central","agriculture","Scheme","SHC_Guidelines.pdf","AGR-04","Para 2","P3","...","Free soil testing.","https://soilhealth.dac.gov.in/","Year-round",
      [{"criterion":"All farmers with land"}],["Submit sample"],["Land Record"],["Agri Office"],{"requiresFarmer":True}),
    S("pmksy","PM Krishi Sinchai","💧","central","agriculture","Irrigation","PMKSY_Guidelines.pdf","AGR-05","Sec 2","P4","...","Subsidies for micro-irrigation.","https://pmksy.gov.in/","Year-round",
      [{"criterion":"All farmers"}],["Apply to State Dept"],["Aadhaar","Land Record"],["Agri Dept"],{"requiresFarmer":True}),
    S("enam","e-NAM","📦","central","agriculture","Mandi","eNAM_Guidelines.pdf","AGR-06","Sec 1","P2","...","Online trading platform.","https://enam.gov.in/","Year-round",
      [{"criterion":"All farmers & traders"}],["Register online"],["Aadhaar","Bank details"],["Mandi"],{"requiresFarmer":True}),
    S("nfsm","National Food Security Mission","🌾","central","agriculture","Mission","NFSM_Guidelines.pdf","AGR-07","Sec 3","P5","...","Subsidized seeds & tools.","https://nfsm.gov.in/","Year-round",
      [{"criterion":"Farmers in NFSM districts"}],["Register at office"],["Aadhaar","Land Record"],["KVK"],{"requiresFarmer":True}),
    S("pkvy","Paramparagat Krishi Vikas","🌿","central","agriculture","Organic","PKVY_Guidelines.pdf","AGR-08","Para 4","P10","...","Organic farming clusters.","https://pkvy.dac.gov.in/","Year-round",
      [{"criterion":"Group of 20+ farmers"}],["Form cluster"],["Aadhaar"],["Agri Office"],{"requiresFarmer":True}),
    S("pm-mmsy","PM Matsya Sampada","🐟","central","agriculture","Fisheries","PMMSY_Guidelines.pdf","AGR-09","Sec 1","P3","...","Development of fisheries.","https://dof.gov.in/","Year-round",
      [{"criterion":"Fishermen/Fish farmers"}],["Submit project"],["Aadhaar"],["Fisheries Dept"],{"requiresFarmer":True}),
    S("rlp","Rashtriya Krishi Vikas","🚜","central","agriculture","Grant","RKVY_Guidelines.pdf","AGR-10","Sec 2","P4","...","Incentivizing state agri spend.","https://rkvy.nic.in/","Year-round",
      [{"criterion":"State project beneficiaries"}],["Via State Dept"],["Aadhaar"],["State Govt"],{"requiresFarmer":True}),

    # === EDUCATION (12) ===
    S("css","Central Scholarships","🎓","central","education","Scholarship","CSS_Guidelines.pdf","EDU-01","Cl 6.2","P12","...","Scholarship for income < 4.5L.","https://scholarships.gov.in/","Dec 2026",
      [{"criterion":"Income < 4.5L"},{"criterion":"Enrolled in college"}],["Apply on NSP"],["Marksheet","Income Cert"],["NSP"],{"requiresStudent":True,"maxIncome":450000}),
    S("sc-scholarship","Post Matric SC","🎓","central","education","Caste-based","SC_PostMatric.pdf","EDU-02","Cl 4.1","P5","...","Aid for SC students (income < 2.5L).","https://scholarships.gov.in/","Oct 2026",
      [{"criterion":"SC Caste"},{"criterion":"Income < 2.5L"}],["Apply on NSP"],["Caste Cert","Income Cert"],["Social Welfare"],{"requiresStudent":True,"requiresCaste":"SC","maxIncome":250000}),
    S("st-fellowship","National ST Fellowship","🏹","central","education","Caste-based","ST_Fellowship.pdf","EDU-03","Cl 2.1","P3","...","Fellowships for ST (income < 6L).","https://tribal.nic.in/","Nov 2026",
      [{"criterion":"ST Caste"},{"criterion":"Income < 6L"}],["Apply on NSP"],["Caste Cert","Income Cert"],["Tribal Dept"],{"requiresStudent":True,"requiresCaste":"ST","maxIncome":600000}),
    S("obc-scholarship","Pre-Matric OBC","📚","central","education","Caste-based","OBC_PreMatric.pdf","EDU-04","Sec 2","P3","...","Aid for OBC students (income < 2.5L).","https://scholarships.gov.in/","Nov 2026",
      [{"criterion":"OBC Caste"},{"criterion":"Income < 2.5L"}],["Apply via School"],["OBC Cert","Income Cert"],["School"],{"requiresStudent":True,"requiresCaste":"OBC","maxIncome":250000}),
    S("pm-vidyalaxmi","PM-Vidyalaxmi","🎓","central","education","Loan","Vidyalaxmi_Guidelines.pdf","EDU-05","Sec 1","P1","...","Interest-free loans up to 10L.","https://vidyalaxmi.co.in/","Dec 2026",
      [{"criterion":"Meritorious student"}],["Apply on portal"],["Admission proof"],["Vidyalaxmi"],{"requiresStudent":True}),
    S("mdm","Mid-Day Meal","🍱","central","education","Nutrition","MDM_Guidelines.pdf","EDU-06","Sec 2","P3","...","Free meals for Class I-VIII.","https://mdm.nic.in/","Year-round",
      [{"criterion":"Govt school student"}],["Auto-enroll"],["School ID"],["School"],{"requiresStudent":True}),
    S("nmmss","NMMSS Scholarship","🏅","central","education","Merit","NMMSS_Guidelines.pdf","EDU-07","Sec 3","P4","...","12,000/year for EWS (income < 3.5L).","https://scholarships.gov.in/","Nov 2026",
      [{"criterion":"Income < 3.5L"},{"criterion":"55% in Class VIII"}],["Clear exam","Apply on NSP"],["Marksheet","Income Cert"],["Education Dept"],{"requiresStudent":True,"maxIncome":350000}),
    S("topclass-sc","Top Class SC","🎓","central","education","Premium","SC_TopClass.pdf","EDU-08","Sec 1","P2","...","Full fee for IITs/IIMs (income < 8L).","https://scholarships.gov.in/","Oct 2026",
      [{"criterion":"SC Caste"},{"criterion":"Income < 8L"}],["Apply on NSP"],["Admission letter","Caste Cert"],["NSP"],{"requiresStudent":True,"requiresCaste":"SC","maxIncome":800000}),
    S("pm-research","PM Research Fellowship","🧪","central","education","Research","PMRF_Guidelines.pdf","EDU-09","Sec 2","P4","...","Direct entry to PhD with 70k-80k stipend.","https://pmrf.in/","Year-round",
      [{"criterion":"GATE/NET qualified"}],["Apply to IITs"],["GATE Score"],["IIT/IISc"],{"requiresStudent":True}),
    S("inspire","INSPIRE Scholarship","🔬","central","education","Science","INSPIRE_Guidelines.pdf","EDU-10","Sec 1","P2","...","Scholarship for Basic Science (top 1%).","https://online-inspire.gov.in/","Oct 2026",
      [{"criterion":"Top 1% in Class XII"}],["Apply online"],["Marksheet"],["DST"],{"requiresStudent":True}),
    S("kvpy","Kishore Vaigyanik","🧬","central","education","Science","KVPY_Guidelines.pdf","EDU-11","Sec 3","P5","...","Fellowship for science students.","https://kvpy.iisc.ernet.in/","Nov 2026",
      [{"criterion":"Clear KVPY exam"}],["Apply online"],["Admit Card"],["IISc"],{"requiresStudent":True}),
    S("bridge-course","Bridge Course for Minorities","📖","central","education","Targeted","Minority_EDU.pdf","EDU-12","Sec 4","P6","...","Bridging formal and informal education.","https://minorityaffairs.gov.in/","Year-round",
      [{"criterion":"Minority student"}],["Apply at centre"],["Aadhaar"],["Study Centre"],{"requiresStudent":True}),

    # === HEALTH (10) ===
    S("pm-jay","PM-JAY","🏥","central","health","Insurance","PMJAY_Guidelines.pdf","HLTH-01","Sec 4.1","P9","...","₹5 lakh health cover.","https://pmjay.gov.in/","Year-round",
      [{"criterion":"SECC listed family"}],["Get card"],["Ration Card"],["Hospitals"],{"defaultMatch":True}),
    S("jsy","Janani Suraksha","🤰","central","health","Maternity","JSY_Guidelines.pdf","HLTH-02","Sec 2","P3","...","₹1400 rural/₹1000 urban for delivery.","https://nhm.gov.in/","Year-round",
      [{"criterion":"Pregnant women"}],["Register at PHC"],["MCP Card"],["PHC/CHC"],{}),
    S("pm-mvy","PM Matru Vandana","👶","central","health","Maternity","PMMVY_Guidelines.pdf","HLTH-03","Sec 4","P6","...","₹5,000 for first child.","https://pmmvy.nic.in/","Year-round",
      [{"criterion":"Pregnant (1st child)"}],["Apply at Anganwadi"],["Aadhaar","MCP"],["Anganwadi"],{}),
    S("janaushadhi","PM Janaushadhi","💊","central","health","Generic","PMBJP_Guidelines.pdf","HLTH-04","Sec 1","P2","...","Medicines at 50-90% cheaper.","https://janaushadhi.gov.in/","Year-round",
      [{"criterion":"All citizens"}],["Visit store"],["Prescription"],["Med Stores"],{"alwaysInclude":True}),
    S("mission-indradhanush","Mission Indradhanush","💉","central","health","Vaccine","MI_Guidelines.pdf","HLTH-05","Sec 1","P2","...","Full immunization for <2 yrs.","https://nhm.gov.in/","Year-round",
      [{"criterion":"Children < 2 yrs"}],["Visit Health Centre"],["MCP Card"],["PHC"],{}),
    S("rbsk","Bal Swasthya","👶","central","health","Screening","RBSK_Guidelines.pdf","HLTH-06","Sec 2","P3","...","Free health screening 0-18 yrs.","https://nhm.gov.in/","Year-round",
      [{"criterion":"All children 0-18 yrs"}],["School screen"],["School ID"],["Schools"],{}),
    S("nvbdcp","Vector Borne Control","🦟","central","health","Disease","NVBDCP_Rules.pdf","HLTH-07","Sec 3","P5","...","Free treatment for Malaria/Dengue.","https://nvbdcp.gov.in/","Year-round",
      [{"criterion":"All patients"}],["Visit Hospital"],["Report"],["Hospitals"],{"alwaysInclude":True}),
    S("rmnch","RMNCH+A","👩","central","health","Family","RMNCH_Rules.pdf","HLTH-08","Sec 1","P2","...","Reproductive and Child Health services.","https://nhm.gov.in/","Year-round",
      [{"criterion":"Mothers/Children"}],["Visit Health Centre"],["Aadhaar"],["PHC"],{}),
    S("ntcp","Tobacco Control","🚭","central","health","Wellness","NTCP_Rules.pdf","HLTH-09","Sec 2","P3","...","Cessation services and counseling.","https://ntcp.nhp.gov.in/","Year-round",
      [{"criterion":"All citizens"}],["Visit Centre"],["ID"],["Wellness Centres"],{"alwaysInclude":True}),
    S("ayush-mission","National AYUSH Mission","🧘","central","health","Ayurveda","AYUSH_Rules.pdf","HLTH-10","Sec 1","P2","...","Subsidies for AYUSH medicines/treatments.","https://ayush.gov.in/","Year-round",
      [{"criterion":"All citizens"}],["Visit AYUSH hospital"],["ID"],["AYUSH Centres"],{"alwaysInclude":True}),

    # === HOUSING & INFRA (8) ===
    S("pmay-u","PMAY (Urban)","🏙️","central","housing","Urban","PMAYU_Guidelines.pdf","HSG-01","Cl 7.1","P18","...","Subsidy for income < 6L.","https://pmaymis.gov.in/","Mar 2026",
      [{"criterion":"Income < 6L"},{"criterion":"No pucca house"}],["Apply online"],["Income proof"],["ULB"],{"maxIncome":600000}),
    S("pmay-g","PMAY (Gramin)","🏡","central","housing","Rural","PMAYG_Guidelines.pdf","HSG-02","Sec 3","P5","...","₹1.2 Lakh for rural house.","https://pmayg.nic.in/","Year-round",
      [{"criterion":"Houseless (SECC list)"}],["Verify at Panchayat"],["Aadhaar"],["Gram Panchayat"],{}),
    S("sbm-g","Swachh Bharat (Gramin)","🚻","central","housing","Sanitation","SBMG_Guidelines.pdf","HSG-03","Sec 4","P6","...","₹12,000 for toilet.","https://sbm.gov.in/","Year-round",
      [{"criterion":"BPL family"}],["Apply at Panchayat"],["Aadhaar"],["Gram Panchayat"],{}),
    S("ujjwala","PM Ujjwala","🔥","central","housing","Energy","PMUY_Guidelines.pdf","HSG-04","Sec 2","P3","...","Free gas connection (BPL women).","https://pmujjwalayojana.com/","Year-round",
      [{"criterion":"BPL Women"}],["Apply at Gas Agency"],["BPL Card"],["Gas Distributor"],{}),
    S("saubhagya","Saubhagya Electricity","💡","central","housing","Power","Saubhagya_Rules.pdf","HSG-05","Sec 1","P2","...","Free electricity connection (BPL).","https://saubhagya.gov.in/","Year-round",
      [{"criterion":"BPL family"}],["Register at camp"],["Aadhaar"],["DISCOM"],{}),
    S("jjm","Jal Jeevan Mission","🚰","central","housing","Water","JJM_Rules.pdf","HSG-06","Sec 2","P4","...","Tap water connection to every home.","https://jaljeevanmission.gov.in/","Year-round",
      [{"criterion":"All households"}],["Apply to Panchayat"],["Aadhaar"],["Gram Panchayat"],{"alwaysInclude":True}),
    S("pm-svanidhi","PM SVANidhi","🛒","central","housing","Loan","SVANidhi_Rules.pdf","HSG-07","Sec 2","P3","...","₹10k-50k loan for vendors.","https://pmsvanidhi.mohua.gov.in/","Year-round",
      [{"criterion":"Street vendors"}],["Apply online"],["Vendor ID"],["ULB"],{}),
    S("amrut","AMRUT","🏙️","central","housing","Infra","AMRUT_Rules.pdf","HSG-08","Sec 1","P2","...","Urban transformation: water/sewer/parks.","https://amrut.gov.in/","Year-round",
      [{"criterion":"Urban residents"}],["Auto-benefit"],["Property Tax ID"],["Municipal Corp"],{"alwaysInclude":True}),

    # === EMPLOYMENT & SKILLS (10) ===
    S("mgnrega","MGNREGA","💼","central","employment","Manual","NREGA_Rules.pdf","EMP-01","Sec 3","P4","...","100 days job card.","https://nrega.nic.in/","Year-round",
      [{"criterion":"Rural household"}],["Apply job card"],["Aadhaar"],["Gram Panchayat"],{"alwaysInclude":True}),
    S("ews-quota","EWS Reservation","💰","central","employment","Quota","EWS_Rules.pdf","EMP-02","Para 2","P2","...","10% quota for income < 8L.","https://india.gov.in/","Year-round",
      [{"criterion":"Income < 8L"},{"criterion":"Not SC/ST/OBC"}],["Get cert"],["ITR/Income"],["Tehsildar"],{"maxIncome":800000}),
    S("obc-quota","OBC Reservation","📜","central","employment","Quota","OBC_Rules.pdf","EMP-03","Sec 3","P4","...","27% quota for income < 8L.","https://ncbc.nic.in/","Year-round",
      [{"criterion":"OBC Category"},{"criterion":"Income < 8L"}],["Get cert"],["Caste/Income"],["Tehsildar"],{"requiresCaste":"OBC","maxIncome":800000}),
    S("pmkvy-skills","PMKVY Training","🛠️","central","employment","Skill","PMKVY_Rules.pdf","EMP-04","Sec 2","P4","...","Free skill training 15-45 yrs.","https://pmkvyofficial.org/","Year-round",
      [{"criterion":"Age 15-45"}],["Find centre"],["Aadhaar"],["Skill Centres"],{"alwaysInclude":True}),
    S("mudra-loans","Mudra Loans","🏪","central","employment","Business","Mudra_Rules.pdf","EMP-05","Cl 1.2","P2","...","No-collateral loans up to 10L.","https://mudra.org.in/","Year-round",
      [{"criterion":"Micro enterprises"}],["Apply at bank"],["Biz Plan"],["Banks"],{}),
    S("startup-india-ben","Startup India","🚀","central","employment","Tax","Startup_Rules.pdf","EMP-06","Sec 2","P3","...","Tax breaks for startups.","https://startupindia.gov.in/","Year-round",
      [{"criterion":"DPIIT Recognized"}],["Register online"],["Incorporation"],["DPIIT"],{}),
    S("standup-india-ben","Stand-Up India","🤝","central","employment","Gender","StandUp_Rules.pdf","EMP-07","Sec 1","P2","...","Loans for SC/ST/Women.","https://standupmitra.in/","Year-round",
      [{"criterion":"SC/ST or Woman"}],["Apply at bank"],["Biz Plan"],["Banks"],{"requiresCaste":"SC/ST"}),
    S("pmegp-subsidy","PMEGP Subsidy","💼","central","employment","Subsidy","PMEGP_Rules.pdf","EMP-08","Sec 3","P5","...","25-35% subsidy for micro-biz.","https://kviconline.gov.in/","Year-round",
      [{"criterion":"Age 18+"}],["Apply on portal"],["Project Report"],["KVIC"],{}),
    S("ddu-gky-skills","DDU-GKY","🛠️","central","employment","Rural","DDUGKY_Rules.pdf","EMP-09","Sec 2","P3","...","Free training for rural poor.","https://ddugky.gov.in/","Year-round",
      [{"criterion":"Rural poor youth"}],["Join centre"],["Aadhaar"],["Training Centre"],{}),
    S("nrlm-shg","NRLM SHG","👩","central","employment","Groups","NRLM_Rules.pdf","EMP-10","Sec 2","P3","...","Livelihood support for women.","https://aajeevika.gov.in/","Year-round",
      [{"criterion":"Rural women group"}],["Form SHG"],["Bank A/c"],["Blocks"],{}),

    # === SOCIAL SECURITY & FINANCIAL (10) ===
    S("apy","Atal Pension","🧓","central","finance","Pension","APY_Rules.pdf","FIN-01","Sec 1","P2","...","Pension up to ₹5k after 60.","https://npscra.nsdl.co.in/","Year-round",
      [{"criterion":"Age 18-40"}],["Open account"],["Aadhaar"],["Banks"],{}),
    S("pmjjby","PM Jeevan Jyoti","🛡️","central","finance","Life","PMJJBY_Rules.pdf","FIN-02","Sec 1","P2","...","₹2 lakh life insurance.","https://jansuraksha.gov.in/","Year-round",
      [{"criterion":"Age 18-50"}],["Auto-debit"],["Aadhaar"],["Banks"],{"alwaysInclude":True}),
    S("pmsby","PM Suraksha Bima","🛡️","central","finance","Accident","PMSBY_Rules.pdf","FIN-03","Sec 1","P2","...","₹2 lakh accident insurance.","https://jansuraksha.gov.in/","Year-round",
      [{"criterion":"Age 18-70"}],["Auto-debit"],["Aadhaar"],["Banks"],{"alwaysInclude":True}),
    S("nsap-oldage","NSAP Old Age","🧓","central","finance","BPL","NSAP_Rules.pdf","FIN-04","Sec 2","P3","...","Pension for BPL seniors (60+).","https://nsap.nic.in/","Year-round",
      [{"criterion":"Age 60+"},{"criterion":"BPL"}],["Apply at block"],["BPL Card"],["Block Office"],{}),
    S("nsap-disability","NSAP Disability","♿","central","finance","BPL","NSAP_Rules.pdf","FIN-05","Sec 2","P3","...","Pension for disabled BPL.","https://nsap.nic.in/","Year-round",
      [{"criterion":"80% Disability"},{"criterion":"BPL"}],["Medical cert"],["BPL Card"],["Social Welfare"],{}),
    S("legal-aid-free","Legal Aid","⚖️","central","finance","Law","NALSA_Rules.pdf","FIN-06","Sec 12","P8","...","Free legal aid for SC/ST/Women.","https://nalsa.gov.in/","Year-round",
      [{"criterion":"SC/ST or Woman"}],["Apply at DLSA"],["Aadhaar"],["DLSA"],{"requiresCaste":"SC/ST"}),
    S("aay-ration","Antyodaya Anna","🍚","central","finance","Food","AAY_Rules.pdf","FIN-07","Sec 2","P3","...","35kg/month foodgrains for poorest.","https://dfpd.gov.in/","Year-round",
      [{"criterion":"Poorest of poor"}],["Get ration card"],["Aadhaar"],["PDS Shop"],{}),
    S("digital-literacy","Digital Saksharta","💻","central","finance","Skill","PMGDISHA_Rules.pdf","FIN-08","Sec 1","P2","...","Free digital literacy training.","https://digitalindia.gov.in/","Year-round",
      [{"criterion":"Rural household"}],["Visit CSC"],["Aadhaar"],["CSC"],{"alwaysInclude":True}),
    S("sc-st-atrocity","SC/ST Protection","⚖️","central","finance","Law","PoA_Act.pdf","FIN-09","Sec 3","P5","...","Compensation for atrocity victims.","https://socialjustice.gov.in/","Year-round",
      [{"criterion":"SC/ST victim"}],["File FIR"],["Caste Cert"],["Police"],{"requiresCaste":"SC/ST"}),
    S("pm-gky-relief","Garib Kalyan Relief","🍚","central","finance","Crisis","PMGKY_Rules.pdf","FIN-10","Sec 1","P2","...","Emergency relief: free rations.","https://india.gov.in/","Crisis",
      [{"criterion":"BPL/AAY"}],["Auto-benefit"],["Ration Card"],["PDS Shop"],{}),
]

output = {
    "version": "3.0.0",
    "lastUpdated": "2026-03-24",
    "totalSchemes": len(schemes),
    "schemes": schemes
}

# Use relative path to project data folder
base_dir = os.path.dirname(os.path.abspath(__file__))
# If in /tmp, let's just write to the target directly
out_path = r"c:\Users\HP\Desktop\new\data\schemes.json"

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Generated {len(schemes)} schemes to {out_path}")
