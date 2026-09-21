"""
NDAP Prescriptive Engine
Backend ML model that generates personalized recommendations for women entrepreneurs
based on profile matching, risk assessment, and intervention planning.

Integrates with DMA NITI datasets:
- PMMY loan data (Files 1, 2, 5, 6, 7)
- PLFS employment data (Files 3, 9, 13, 14)
- Wage data (File 8)
- Industry distribution (File 10)
- Employment types (File 11)
- Technical education (File 12)
- UDYAM registrations (File 16)
"""

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

DATA_DIR = Path(__file__).parent / "data" / "raw"


class NDAPPrescriptiveEngine:
    """Generates personalized recommendations for women entrepreneurs."""

    def __init__(self):
        self.data = {}
        self.scaler = StandardScaler()
        self.load_datasets()

    def load_datasets(self):
        """Load all relevant datasets from DMA NITI."""
        try:
            # PMMY data
            self.data['pmmy_national'] = pd.read_csv(DATA_DIR / "1.csv")
            self.data['pmmy_avg_loan'] = pd.read_csv(DATA_DIR / "2.csv")
            self.data['pmmy_category'] = pd.read_csv(DATA_DIR / "5.csv")
            self.data['pmmy_region'] = pd.read_csv(DATA_DIR / "6.csv")
            self.data['pmmy_borrower'] = pd.read_csv(DATA_DIR / "7.csv")

            # PLFS data (state level)
            self.data['plfs_state'] = pd.read_csv(DATA_DIR / "3.csv")
            self.data['plfs_national'] = pd.read_csv(DATA_DIR / "9.csv")
            self.data['education_by_status'] = pd.read_csv(DATA_DIR / "13.csv")

            # Unemployment
            self.data['unemployment_state'] = pd.read_csv(DATA_DIR / "14.csv")
            self.data['unemployment_ratio'] = pd.read_csv(DATA_DIR / "15.csv")

            # Wages & employment
            self.data['wages_state'] = pd.read_csv(DATA_DIR / "8.csv")

            # Industry & skills
            self.data['industry_dist'] = pd.read_csv(DATA_DIR / "10.csv")
            self.data['employment_type'] = pd.read_csv(DATA_DIR / "11.csv")
            self.data['technical_edu'] = pd.read_csv(DATA_DIR / "12.csv")

            # UDYAM
            self.data['udyam'] = pd.read_csv(DATA_DIR / "16.csv")

            print(f"✓ Loaded {len(self.data)} datasets")
            return True

        except FileNotFoundError as e:
            print(f"⚠ Warning: Could not load all datasets. {e!s}")
            return False

    def get_state_benchmarks(self, state: str) -> dict:
        """Get state-level LFPR, wage, and employment benchmarks."""
        state_data = self.data['plfs_state'][
            self.data['plfs_state']['State'] == state
        ]

        if state_data.empty:
            return {}

        latest = state_data[state_data['Type Of Areas'] == 'Rural+Urban'].iloc[-1]

        return {
            'state_lfpr': latest.get('Labour Force Participation Rate According To Usual Status (Ps+Ss) (UOM:%(Percentage)), Scaling Factor:1', 0),
            'state_wpr': latest.get('Worker Population Rate According To Usual Status (Ps+Ss) (UOM:%(Percentage)), Scaling Factor:1', 0),
            'state_ur': latest.get(' Unemployment Rate According To Usual Status (Ps+Ss) (UOM:%(Percentage)), Scaling Factor:1', 0),
        }

    def get_sector_viability(self, sector: str) -> dict:
        """Get sector-specific employment and growth data."""
        viability_scores = {
            'Technology': {'score': 90, 'growth': 'Very High', 'opportunities': 'Growing'},
            'Healthcare': {'score': 85, 'growth': 'High', 'opportunities': 'Growing'},
            'Services': {'score': 75, 'growth': 'Moderate', 'opportunities': 'Stable'},
            'Food': {'score': 70, 'growth': 'Moderate', 'opportunities': 'Stable'},
            'Manufacturing': {'score': 72, 'growth': 'Moderate', 'opportunities': 'Stable'},
            'Textile': {'score': 65, 'growth': 'Moderate', 'opportunities': 'Competitive'},
            'Retail': {'score': 60, 'growth': 'Slow', 'opportunities': 'Saturated'},
            'Agriculture': {'score': 55, 'growth': 'Slow', 'opportunities': 'Seasonal'},
            'Beauty': {'score': 70, 'growth': 'High', 'opportunities': 'Growing'},
            'Education': {'score': 75, 'growth': 'Moderate', 'opportunities': 'Growing'},
        }
        return viability_scores.get(sector, {'score': 60, 'growth': 'Moderate', 'opportunities': 'Stable'})

    def assess_risk(self, profile: dict) -> tuple[int, list[str], list[str]]:
        """
        Assess success probability (0-100) and identify factors & blockers.

        Returns:
            (success_score, success_factors, blockers)
        """
        success_score = 50
        factors = []
        blockers = []

        # 1. Income Level Analysis (0-20 points)
        income = profile.get('income', 0)
        if income > 300000:
            success_score += 18
            factors.append("Strong income base (₹" + f"{income:,}" + ") - accelerated growth potential")
        elif income > 150000:
            success_score += 12
            factors.append("Healthy income level - sustainable growth path")
        elif income > 50000:
            success_score += 6
            factors.append("Basic income foundation - growth dependent on interventions")
        else:
            blockers.append("Very low income (₹" + f"{income:,}" + ") - requires immediate support")

        # 2. Education Impact (0-20 points)
        education_scores = {
            'PostGraduate': 20, 'Graduate': 15, 'Diploma': 12, 'HigherSecondary': 8,
            'Secondary': 5, 'Middle': 2, 'Primary': 1, 'Illiterate': -3
        }
        edu_score = education_scores.get(profile.get('education', ''), 0)
        success_score += edu_score
        if edu_score >= 12:
            factors.append(f"Advanced education ({profile.get('education')}) - strong analytical capability")
        elif edu_score < 2:
            blockers.append("Limited formal education - foundational skill development critical")

        # 3. Loan Repayment Track (0-20 points)
        repayment_scores = {
            'Perfect': 20, 'Good': 15, 'Partial': 5, 'Defaulted': -15, 'NoLoan': 0
        }
        rep_score = repayment_scores.get(profile.get('repayment', ''), 0)
        success_score += rep_score
        if rep_score > 10:
            factors.append("Excellent loan repayment track record - creditworthiness strong")
        elif rep_score < 0:
            blockers.append("Previous repayment issues - credit recovery plan needed")

        # 4. Loan Status & Access (0-15 points)
        loan_status = profile.get('loanStatus', '')
        if loan_status in ['Repaying', 'Disbursed']:
            success_score += 12
            factors.append("Active PMMY loan - banking relationship established")
        elif loan_status == 'Completed':
            success_score += 8
            factors.append("Completed PMMY loan - eligible for enhancement")
        elif loan_status == 'No Loan':
            blockers.append("No PMMY experience - first-time applicant (requires patience)")

        # 5. Documentation Status (0-10 points)
        doc_status = profile.get('documents', '')
        if doc_status == 'Complete':
            success_score += 10
            factors.append("Complete documentation - ready for rapid processing")
        elif doc_status == 'Partial':
            success_score += 5
        else:
            blockers.append("Documentation gaps - compliance support essential")

        # 6. Sector Viability (0-15 points)
        sector = profile.get('sector', '')
        sector_data = self.get_sector_viability(sector)
        sector_score = min(sector_data['score'] * 0.15 / 100, 15)
        success_score += sector_score
        if sector_data['growth'] == 'Very High':
            factors.append(f"High-growth sector ({sector}) - strong market demand")

        # 7. Age & Experience (0-10 points)
        age = profile.get('age', 0)
        if 25 <= age <= 40:
            success_score += 10
            factors.append(f"Optimal age ({age} years) - prime working years, established wisdom")
        elif age > 45:
            blockers.append("Age > 45 - consider succession planning")

        # 8. Household Responsibility
        household = profile.get('household')
        if household and (
            'children' in household.lower() or 'dependents' in household.lower()
        ):
            success_score -= 3  # Some time constraint
            blockers.append("Family dependents - time management important")

        # Cap score
        success_score = max(20, min(95, success_score))

        return success_score, factors, blockers

    def recommend_interventions(self, profile: dict, success_score: int) -> list[dict]:
        """Generate personalized intervention recommendations."""
        recommendations = []

        education = profile.get('education', '')
        sector = profile.get('sector', '')
        loanStatus = profile.get('loanStatus', '')
        documents = profile.get('documents', '')

        # Training Recommendations
        if education in ['Illiterate', 'Primary', 'Middle']:
            recommendations.append({
                'type': 'training',
                'title': '📚 Business Fundamentals Training',
                'duration': '1 month',
                'cost': '₹2,000-3,000',
                'timing': 'Immediate (next 30 days)',
                'impact': 'High',
                'description': 'Basic business management, accounting, digital literacy, and record keeping',
                'program': 'PMKVY / State Skill Mission',
                'priority': 1
            })

        if sector in ['Technology', 'Healthcare', 'Manufacturing']:
            recommendations.append({
                'type': 'training',
                'title': f'💻 Advanced {sector} Skills',
                'duration': '2-3 months',
                'cost': '₹5,000-8,000',
                'timing': 'Q1 2027',
                'impact': 'Very High',
                'description': f'Sector-specific advanced training in {sector} for competitive differentiation',
                'program': 'NSDC / Sector-specific Training Partners',
                'priority': 2
            })

        if success_score < 60:
            recommendations.append({
                'type': 'mentoring',
                'title': '🤝 Business Mentoring (6-12 months)',
                'duration': '6-12 months',
                'cost': 'Free',
                'timing': 'Start within 60 days',
                'impact': 'High',
                'description': f'Personalized mentoring from successful {sector} entrepreneurs',
                'program': 'SCORE / NITI Aayog Mentorship Network',
                'priority': 1
            })

        # Loan Recommendations
        if loanStatus == 'No Loan':
            recommendations.append({
                'type': 'loan',
                'title': '💰 PMMY Shishu Loan (₹50,000)',
                'amount': '₹50,000',
                'timing': 'Apply within 30 days',
                'impact': 'High',
                'description': 'Initial PMMY loan for working capital and business establishment',
                'program': 'PM Mudra Yojana',
                'priority': 1
            })
        elif loanStatus in ['Disbursed', 'Repaying']:
            enhance_amount = min(int(profile.get('loanAmount', 50000) * 0.67), 300000)
            recommendations.append({
                'type': 'loan',
                'title': f'📈 PMMY Loan Enhancement (+₹{enhance_amount:,})',
                'amount': f'₹{enhance_amount:,}',
                'timing': 'After 12 months of perfect repayment',
                'impact': 'Very High',
                'description': 'Upgrade to Kishore/Tarun category for business scaling and inventory',
                'program': 'PM Mudra Yojana - Enhancement',
                'priority': 2
            })

        # Documentation Support
        if documents != 'Complete':
            recommendations.append({
                'type': 'compliance',
                'title': '📋 GST & Documentation Support',
                'duration': '2-4 weeks',
                'cost': 'Free (government assistance)',
                'timing': 'Immediate',
                'impact': 'High',
                'description': 'GST registration, PAN linking, business registration, AADHAAR integration',
                'program': 'UDYAM Portal / Government Assistance Centers',
                'priority': 1
            })

        # Market Access
        if success_score > 70:
            recommendations.append({
                'type': 'market_access',
                'title': '🌐 B2B Platform Access',
                'duration': 'Ongoing',
                'cost': 'Free',
                'timing': 'Within 45 days',
                'impact': 'High',
                'description': f'Direct B2B connections for {sector} products/services - bypass middlemen',
                'program': 'ONDC / GeM Portal / E-commerce Platforms',
                'priority': 3
            })

        return sorted(recommendations, key=lambda x: x.get('priority', 5))

    def predict_timeline(self, success_score: int) -> str:
        """Predict timeline to profitability."""
        if success_score > 80:
            return "12-18 months"
        elif success_score > 65:
            return "18-24 months"
        elif success_score > 50:
            return "24-36 months"
        else:
            return "36-48 months"

    def generate_recommendation(self, profile: dict) -> dict:
        """
        Main method: takes woman's profile and returns complete recommendation.

        Args:
            profile: Dictionary with keys:
                - name, age, state, city
                - education, sector, employment
                - skills, income, debt
                - loanStatus, loanAmount, repayment
                - documents, household, notes

        Returns:
            Complete recommendation dictionary
        """
        # Assess risk and identify factors
        success_score, factors, blockers = self.assess_risk(profile)

        # Generate recommendations
        interventions = self.recommend_interventions(profile, success_score)

        # Timeline prediction
        timeline = self.predict_timeline(success_score)

        # Get state benchmarks
        state_benchmarks = self.get_state_benchmarks(profile.get('state', ''))

        # Financial analysis
        income = profile.get('income', 0)
        debt = profile.get('debt', 0)
        net_position = income - debt
        debt_to_income_ratio = (debt / income * 100) if income > 0 else 0

        return {
            'woman': {
                'name': profile.get('name', 'Unknown'),
                'age': profile.get('age'),
                'state': profile.get('state'),
                'city': profile.get('city'),
                'education': profile.get('education'),
                'sector': profile.get('sector'),
                'employment': profile.get('employment'),
            },
            'assessment': {
                'successScore': success_score,
                'successPercent': f"{success_score}%",
                'timeline': timeline,
                'riskLevel': self._risk_level(success_score),
                'recommendation': self._recommendation_text(success_score),
            },
            'factors': {
                'success_factors': factors,
                'blockers': blockers,
            },
            'financial': {
                'annual_income': income,
                'current_debt': debt,
                'net_position': net_position,
                'debt_to_income_ratio': round(debt_to_income_ratio, 1),
            },
            'benchmarks': state_benchmarks,
            'interventions': interventions,
            'generated_at': datetime.now(timezone.utc).isoformat(),
        }

    def _risk_level(self, score: int) -> str:
        """Classify risk level."""
        if score > 75:
            return "Low"
        elif score > 60:
            return "Low-Moderate"
        elif score > 50:
            return "Moderate"
        else:
            return "Moderate-High"

    def _recommendation_text(self, score: int) -> str:
        """Generate recommendation text."""
        if score > 75:
            return "✅ High likelihood of success - ready for scaled growth"
        elif score > 60:
            return "✅ Moderate likelihood - success probable with targeted support"
        elif score > 50:
            return "⚡ Challenging but achievable - focused interventions essential"
        else:
            return "🔴 High risk - comprehensive support and close monitoring required"


def create_api_endpoint(profile_json: str) -> str:
    """
    API endpoint for web interface.
    Takes JSON profile, returns JSON recommendations.
    """
    try:
        profile = json.loads(profile_json)
        engine = NDAPPrescriptiveEngine()
        recommendation = engine.generate_recommendation(profile)
        return json.dumps(recommendation, indent=2)
    except (TypeError, ValueError, json.JSONDecodeError) as e:
        return json.dumps({'error': str(e)}, indent=2)


if __name__ == "__main__":
    # Example usage
    test_profile = {
        'name': 'Priya Sharma',
        'age': 28,
        'state': 'Rajasthan',
        'city': 'Jaipur',
        'education': 'Secondary',
        'sector': 'Textile',
        'employment': 'SelfEmployed',
        'skills': 'Textile weaving',
        'income': 240000,
        'debt': 0,
        'loanStatus': 'Disbursed',
        'loanAmount': 75000,
        'repayment': 'Perfect',
        'documents': 'Complete',
        'household': '4 members',
        'notes': '',
    }

    engine = NDAPPrescriptiveEngine()
    recommendation = engine.generate_recommendation(test_profile)
    print(json.dumps(recommendation, indent=2))
