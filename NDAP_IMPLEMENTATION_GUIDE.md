# NDAP Intelligence Platform - Complete Implementation Guide

## 🎯 Vision

Transform how governments support women entrepreneurs by moving from **one-size-fits-all schemes** to **data-driven, personalized interventions**.

Instead of treating all women equally, the NDAP platform helps officers identify:
- **Where** each woman stands (current situation)
- **Where** she's heading (risk assessment)
- **Why** that outcome (interpretable factors)
- **What to do** (personalized interventions)

---

## 📊 System Architecture

### Three Integrated Layers

```
┌─────────────────────────────────────────┐
│  Layer 1: Beautiful Interactive UI      │
│  (HTML/CSS/JavaScript Dashboard)        │
│  - Form inputs for woman's profile      │
│  - Real-time validation                 │
│  - Interactive visualizations           │
└──────────────┬──────────────────────────┘
               │ JSON Profile
               ↓
┌─────────────────────────────────────────┐
│  Layer 2: Flask Web Server              │
│  (REST API Endpoints)                   │
│  - /api/recommend                       │
│  - /api/compare                         │
│  - /api/states, /api/sectors            │
│  - /api/dashboard                       │
└──────────────┬──────────────────────────┘
               │ Profile + Calculation
               ↓
┌─────────────────────────────────────────┐
│  Layer 3: ML Recommendation Engine      │
│  (Python + 16 Datasets)                 │
│  - Risk assessment (0-100%)             │
│  - Factor identification                │
│  - Intervention prescription            │
│  - Timeline projection                  │
└─────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /Users/sarasharma/Downloads/womens_economic_empowerment_vscode
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Ensure Data is in Place

The system expects 16 CSV files in `data/raw/`:
```
data/raw/
├── 1.csv  (PMMY national)
├── 2.csv  (PMMY avg loan)
├── 3.csv  (PLFS state)
├── 4.csv  (Vocational training)
├── 5.csv  (PMMY by category)
├── 6.csv  (PMMY by region)
├── 7.csv  (PMMY by borrower)
├── 8.csv  (Wage data)
├── 9.csv  (PLFS national)
├── 10.csv (Industry distribution)
├── 11.csv (Employment types)
├── 12.csv (Technical education)
├── 13.csv (Education by status)
├── 14.csv (Unemployment state)
├── 15.csv (Unemployment ratio)
└── 16.csv (UDYAM registrations)
```

### Step 3: Run the Flask Server

```bash
python ndap_app.py
```

Output:
```
╔════════════════════════════════════════════════════════════════════════════╗
║                 NDAP INTELLIGENCE PLATFORM                                 ║
║         Decision Support System for Women Entrepreneurs                    ║
╚════════════════════════════════════════════════════════════════════════════╝

🚀 Starting Flask Server...
🌐 Open in browser: http://localhost:5000
```

### Step 4: Access the Dashboard

Open in your browser:
```
http://localhost:5000
```

---

## 📋 Using the Platform

### Input a Woman's Profile

The form captures:

**Personal Information:**
- Name, Age
- State, City
- Education Level (Illiterate to Post-Graduate)
- Business Sector (Agriculture to Technology)
- Employment Status (Self-employed, Wage Worker, etc.)
- Skills/Trade

**Financial Information:**
- Annual Income (₹)
- Current Debt (₹)
- PMMY Loan Status (No Loan, Applied, Approved, Disbursed, Repaying, Completed)
- Current Loan Amount (₹)

**Track Record & Readiness:**
- Loan Repayment Track (Perfect, Good, Partial, Defaulted, None)
- Documentation Status (Complete, Partial, Minimal, None)
- Household Size & Dependents

### View Personalized Recommendations

The platform generates:

**1. Success Assessment**
```
Success Probability: 72%
├─ High likelihood of success
├─ Timeline: 18-24 months
└─ Risk Level: Low-Moderate
```

**2. Diagnosis (Why?)**
```
✅ Success Factors:
   • Good loan repayment track record
   • Active PMMY loan (banking access established)
   • Strong income base (₹240,000)

⚠️ Key Blockers:
   • Limited formal training in sector
   • Documentation gaps (GST registration)
   • Market access limited
```

**3. Personalized Interventions**
```
🎓 Training: Sector-specific skills (3 months, ₹8,000)
   → Timing: Q4 2026 | Impact: High | Program: PMKVY

💰 Loan: PMMY Enhancement (+₹50,000)
   → Timing: After 12 months | Impact: Very High

📋 Support: GST & Documentation assistance
   → Timing: Immediate | Impact: High | Cost: Free

🤝 Mentoring: Business mentoring (6-12 months)
   → Timing: Within 60 days | Impact: High | Cost: Free
```

**4. Financial Snapshot**
```
Annual Income: ₹240,000
Current Debt: ₹0
Net Position: ₹240,000
Debt-to-Income Ratio: 0%
```

**5. Income Growth Projection**
```
Interactive 24-month projection showing expected income growth
based on success factors and recommended interventions
```

---

## 🔧 Technical Details

### Recommendation Engine (prescriptive_engine.py)

The Python engine implements 4 phases:

#### Phase 1: Profile Matching
- Finds similar women in datasets
- State + education + sector matching
- Employment trajectory lookup
- Wage benchmarking

#### Phase 2: Risk Assessment (Success Score 0-100)

Factors evaluated:
- **Income Level** (0-20 points)
  - > ₹300K: +18 | > ₹150K: +12 | > ₹50K: +6 | Low: -5
  
- **Education Impact** (0-20 points)
  - Post-Grad: +20 | Graduate: +15 | Diploma: +12 | Secondary: +5
  
- **Loan Repayment** (0-20 points)
  - Perfect: +20 | Good: +15 | Partial: +5 | Defaulted: -15
  
- **Banking Access** (0-15 points)
  - Active loan: +12 | Completed loan: +8
  
- **Documentation** (0-10 points)
  - Complete: +10 | Partial: +5 | Minimal: -5
  
- **Sector Viability** (0-15 points)
  - Tech/Healthcare: ~13 | Manufacturing: ~11 | Textile: ~10
  
- **Age & Experience** (0-10 points)
  - 25-40 years: +10 | > 45 years: -3

#### Phase 3: Explainability (SHAP-ready)
- Top success factors identified
- Specific blockers explained
- Changeable vs. fixed factors distinguished

#### Phase 4: Prescription
- Recommends specific programs (PMMY, PMKVY, NITI Aayog, etc.)
- Suggests training duration & cost
- Proposes timeline for interventions
- Estimates impact on income growth

### API Endpoints

#### `POST /api/recommend`
Generates personalized recommendations.

**Request:**
```json
{
  "name": "Priya Sharma",
  "age": 28,
  "state": "Rajasthan",
  "city": "Jaipur",
  "education": "Secondary",
  "sector": "Textile",
  "employment": "SelfEmployed",
  "skills": "Textile weaving",
  "income": 240000,
  "debt": 0,
  "loanStatus": "Disbursed",
  "loanAmount": 75000,
  "repayment": "Perfect",
  "documents": "Complete",
  "household": "4 members, 2 children"
}
```

**Response:**
```json
{
  "assessment": {
    "successScore": 95,
    "timeline": "12-18 months",
    "riskLevel": "Low"
  },
  "factors": {
    "success_factors": [...],
    "blockers": [...]
  },
  "interventions": [
    {
      "type": "training",
      "title": "Advanced Textile Design",
      "timing": "Q4 2026",
      "impact": "High"
    }
  ]
}
```

#### `GET /api/states`
Returns list of available states for dropdown.

#### `GET /api/sectors`
Returns list of business sectors.

#### `POST /api/compare`
Compares the woman with similar profiles in database.

#### `GET /api/dashboard`
Aggregated statistics for admin dashboard.

---

## 📈 Data Integration

### DMA NITI Datasets Used

| File | Dataset | Purpose |
|------|---------|---------|
| 1 | PMMY National | Loan account trends |
| 2 | PMMY Avg Loan | Loan size benchmarks |
| 3 | PLFS State | LFPR by state & demographics |
| 4 | Vocational Training | Skills availability |
| 5 | PMMY by Category | Women borrower stats |
| 6 | PMMY by Region | Geographic distribution |
| 7 | PMMY by Borrower | Category-wise breakdown |
| 8 | Wage Data | State-sector income benchmarks |
| 9 | PLFS National | Employment participation rates |
| 10 | Industry Distribution | Sector-wise employment |
| 11 | Employment Type | Self-employed vs. wage worker |
| 12 | Technical Education | Skill availability by type |
| 13 | Education by Status | Education-income correlation |
| 14 | Unemployment State | Unemployment by demographics |
| 15 | Unemployment Ratio | State unemployment rates |
| 16 | UDYAM | Business registration data |

---

## 🎯 Key Recommendations

### For Government Officers

**When using the platform:**
1. Fill in woman's profile accurately
2. Review the **Success Probability** - this is data-driven, not subjective
3. Pay attention to **Key Blockers** - these are the actual obstacles to success
4. Follow the **Personalized Interventions** - not generic training for everyone
5. Note the **Timeline** - set realistic expectations
6. Track **Loan Repayment** - it's the strongest predictor of success

**Decision Framework:**
- **Score > 80%:** Ready for scaled growth, consider loan enhancement
- **Score 60-80%:** Support likely to succeed, combine training + loan
- **Score 40-60%:** Needs focused support, start with mentoring + training
- **Score < 40%:** High risk, requires comprehensive package + close monitoring

### For System Administrators

**To improve recommendations:**
1. Continuously feed back on whether predictions matched reality
2. Update dataset with outcomes (loan repaid? business survived? income grew?)
3. Refine sector viability scores based on actual success rates
4. Add state-specific factors that affect outcomes
5. Monitor for equity across castes, religions, geographic areas

---

## 🔮 Future Enhancements

### Phase 7: Individual-Level Data
- Link PMMY borrower IDs to UDYAM registrations
- Track individual loan outcomes over time
- Build individual success/failure profiles

### Phase 8: Causal Inference
- Use doubly robust estimation to identify causal effects
- Determine which interventions actually work
- Not just correlation, but causation

### Phase 9: Dynamic Recommendations
- Update recommendations as woman's status changes
- Adaptive timing based on actual vs. projected progress
- Real-time success probability updates

### Phase 10: Integration with Government Systems
- Connect to PMMY approval systems
- Link to UDYAM registration portal
- Integration with PLFS data collection

### Phase 11: Mobile App
- Field officers can input profiles on tablets
- Offline capability for rural areas
- SMS-based recommendations for women entrepreneurs

### Phase 12: Impact Measurement
- Track outcomes against recommendations
- Measure intervention effectiveness
- Government dashboard showing state-level impact

---

## 📞 Support & Documentation

### File Structure
```
womens_economic_empowerment_vscode/
├── ndap_prescriptive_dashboard.html  ← Beautiful UI (run in browser)
├── prescriptive_engine.py            ← ML recommendation engine
├── ndap_app.py                       ← Flask web server
├── data/
│   └── raw/                          ← 16 CSV datasets
├── outputs/                          ← Generated reports
├── requirements.txt                  ← Python dependencies
└── NDAP_IMPLEMENTATION_GUIDE.md      ← This file
```

### Running Tests

```bash
# Test the recommendation engine directly
python prescriptive_engine.py

# Or run the Flask server
python ndap_app.py
```

### Troubleshooting

**Issue:** "FileNotFoundError: 1.csv not found"
- **Solution:** Ensure all 16 CSV files are in `data/raw/`

**Issue:** Flask server won't start
- **Solution:** Check if port 5000 is already in use. Try: `python ndap_app.py --port 5001`

**Issue:** Recommendations seem inaccurate
- **Solution:** Verify dataset column names match the code. Datasets may use different naming conventions.

---

## 📄 License & Attribution

**Project:** NDAP Intelligence Platform for Women Entrepreneurs  
**Built:** 2026 for women's economic empowerment  
**Data Source:** DMA NITI Government Datasets  
**Powered by:** Python, Flask, scikit-learn, pandas

---

## 🙋 Questions?

The platform is designed to be intuitive. If you have questions about:

- **How to use the UI** → Try the example (Priya Sharma profile)
- **What the scores mean** → See "Success Assessment" section above
- **Why a recommendation** → Look at "Key Blockers" & "Success Factors"
- **How to improve it** → See "Future Enhancements" section

**Remember:** This is a decision support tool, not a decision replacement. Always combine data insights with local expertise and human judgment.

---

*Last Updated: 2026-09-02*  
*Status: Beta - Ready for Field Testing*
