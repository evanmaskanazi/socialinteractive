import datetime
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


@dataclass
class PatientProfile:
    """Enhanced data structure to store comprehensive patient information including country"""
    name: str
    age: int
    country: str
    city: str
    gender: str
    employment_status: str
    exercise_level: str
    mental_state: str
    financial_status: str
    additional_notes: str = ""


class GlobalHealthDatabase:
    """Database of country-specific health statistics and evidence-based treatment recommendations"""

    def __init__(self):
        # Country-specific health statistics and common issues
        self.country_health_data = {
            "united_states": {
                "common_health_issues": ["obesity", "diabetes", "heart_disease", "depression", "anxiety"],
                "mental_health_prevalence": 0.26,  # 26% have mental health issues
                "healthcare_system": "private_insurance",
                "crisis_resources": ["988", "911"],
                "cultural_considerations": ["individualistic_society", "stigma_around_mental_health"],
                "treatment_accessibility": "insurance_dependent",
                "preventive_care_focus": ["annual_checkups", "cancer_screenings", "vaccination"]
            },
            "canada": {
                "common_health_issues": ["depression", "anxiety", "substance_abuse", "heart_disease"],
                "mental_health_prevalence": 0.20,
                "healthcare_system": "universal_healthcare",
                "crisis_resources": ["988", "911"],
                "cultural_considerations": ["multicultural_awareness", "indigenous_health_needs"],
                "treatment_accessibility": "publicly_funded",
                "preventive_care_focus": ["mental_health_screening", "chronic_disease_prevention"]
            },
            "united_kingdom": {
                "common_health_issues": ["depression", "anxiety", "diabetes", "respiratory_disease"],
                "mental_health_prevalence": 0.25,
                "healthcare_system": "nhs",
                "crisis_resources": ["999", "116 123 (Samaritans)"],
                "cultural_considerations": ["class_awareness", "regional_variations"],
                "treatment_accessibility": "free_at_point_of_care",
                "preventive_care_focus": ["nhs_health_checks", "mental_health_first_aid"]
            },
            "australia": {
                "common_health_issues": ["skin_cancer", "mental_health", "obesity", "heart_disease"],
                "mental_health_prevalence": 0.22,
                "healthcare_system": "medicare_plus_private",
                "crisis_resources": ["000", "13 11 14 (Lifeline)"],
                "cultural_considerations": ["indigenous_health_gap", "rural_isolation"],
                "treatment_accessibility": "subsidized_healthcare",
                "preventive_care_focus": ["skin_cancer_screening", "mental_health_plans"]
            },
            "germany": {
                "common_health_issues": ["cardiovascular_disease", "depression", "diabetes", "cancer"],
                "mental_health_prevalence": 0.18,
                "healthcare_system": "statutory_insurance",
                "crisis_resources": ["112", "0800 111 0 111"],
                "cultural_considerations": ["work_life_balance", "privacy_concerns"],
                "treatment_accessibility": "insurance_covered",
                "preventive_care_focus": ["health_checkups", "workplace_wellness"]
            },
            "japan": {
                "common_health_issues": ["cardiovascular_disease", "depression", "suicide_risk", "aging_related"],
                "mental_health_prevalence": 0.15,
                "healthcare_system": "universal_insurance",
                "crisis_resources": ["110", "119"],
                "cultural_considerations": ["mental_health_stigma", "work_stress", "aging_society"],
                "treatment_accessibility": "insurance_covered_limited_mental_health",
                "preventive_care_focus": ["longevity_care", "workplace_stress_management"]
            },
            "india": {
                "common_health_issues": ["diabetes", "cardiovascular_disease", "respiratory_disease", "mental_health"],
                "mental_health_prevalence": 0.13,
                "healthcare_system": "mixed_public_private",
                "crisis_resources": ["100", "108"],
                "cultural_considerations": ["family_centered_care", "traditional_medicine", "stigma"],
                "treatment_accessibility": "variable_access",
                "preventive_care_focus": ["diabetes_prevention", "maternal_health"]
            },
            "brazil": {
                "common_health_issues": ["violence_related_trauma", "infectious_disease", "mental_health", "diabetes"],
                "mental_health_prevalence": 0.18,
                "healthcare_system": "sus_public_system",
                "crisis_resources": ["190", "188"],
                "cultural_considerations": ["family_support", "socioeconomic_disparities"],
                "treatment_accessibility": "public_system_limited_resources",
                "preventive_care_focus": ["infectious_disease_prevention", "violence_prevention"]
            },
            "south_africa": {
                "common_health_issues": ["hiv_aids", "tuberculosis", "mental_health", "violence_trauma"],
                "mental_health_prevalence": 0.16,
                "healthcare_system": "two_tier_system",
                "crisis_resources": ["10177", "112"],
                "cultural_considerations": ["ubuntu_philosophy", "language_diversity", "historical_trauma"],
                "treatment_accessibility": "public_private_divide",
                "preventive_care_focus": ["hiv_prevention", "tb_screening", "trauma_informed_care"]
            },
            "sweden": {
                "common_health_issues": ["depression", "anxiety", "seasonal_affective_disorder",
                                         "cardiovascular_disease"],
                "mental_health_prevalence": 0.17,
                "healthcare_system": "universal_healthcare",
                "crisis_resources": ["112", "90101"],
                "cultural_considerations": ["seasonal_depression", "work_life_balance", "gender_equality"],
                "treatment_accessibility": "publicly_funded",
                "preventive_care_focus": ["mental_health_promotion", "preventive_medicine"]
            },
            "israel": {
                "common_health_issues": ["anxiety", "ptsd", "cardiovascular_disease", "diabetes", "depression"],
                "mental_health_prevalence": 0.21,
                "healthcare_system": "universal_healthcare_with_supplements",
                "crisis_resources": ["100", "101", "1201"],
                "cultural_considerations": ["trauma_informed_care", "military_service_impact",
                                            "multicultural_population", "religious_considerations"],
                "treatment_accessibility": "universal_with_private_options",
                "preventive_care_focus": ["trauma_screening", "stress_management", "community_resilience"]
            },
            "france": {
                "common_health_issues": ["depression", "anxiety", "cardiovascular_disease", "cancer",
                                         "substance_abuse"],
                "mental_health_prevalence": 0.19,
                "healthcare_system": "social_security_system",
                "crisis_resources": ["15", "112", "3114"],
                "cultural_considerations": ["work_life_balance", "social_solidarity", "secularism",
                                            "intellectual_approach_to_therapy"],
                "treatment_accessibility": "highly_subsidized",
                "preventive_care_focus": ["mental_health_destigmatization", "workplace_wellness", "social_medicine"]
            }
        }

        # Age-based treatment effectiveness data (enhanced with country considerations)
        self.age_based_treatments = {
            "young_adult": {
                "most_effective": ["peer_support", "digital_therapy", "group_therapy", "crisis_text_services"],
                "considerations": ["Technology-friendly interventions", "Peer connections crucial",
                                   "Financial constraints common"],
                "country_specific": {
                    "japan": ["work_stress_counseling", "social_anxiety_support"],
                    "india": ["family_therapy_integration", "traditional_medicine_complement"],
                    "sweden": ["seasonal_light_therapy", "student_support_services"],
                    "israel": ["trauma_informed_therapy", "military_transition_support", "multicultural_peer_groups"],
                    "france": ["psychoanalytic_approaches", "university_counseling", "secular_therapy_options"]
                }
            },
            "adult": {
                "most_effective": ["cbt", "family_therapy", "workplace_eap", "community_programs"],
                "considerations": ["Work-life balance issues", "Family responsibilities", "Career pressures"],
                "country_specific": {
                    "germany": ["workplace_wellness_programs", "stress_management"],
                    "united_states": ["insurance_navigation_support", "debt_counseling"],
                    "brazil": ["community_health_workers", "family_integration"],
                    "israel": ["reserve_duty_counseling", "work_security_balance", "multicultural_workplace_support"],
                    "france": ["workplace_rights_advocacy", "social_protection_navigation", "burnout_prevention"]
                }
            },
            "middle_aged": {
                "most_effective": ["individual_therapy", "support_groups", "medical_integration",
                                   "lifestyle_counseling"],
                "considerations": ["Health complications increasing", "Career transitions", "Family caregiving roles"],
                "country_specific": {
                    "japan": ["aging_parent_care_support", "retirement_planning"],
                    "australia": ["skin_cancer_prevention", "rural_telehealth"],
                    "south_africa": ["chronic_disease_management", "family_health_education"],
                    "israel": ["chronic_stress_management", "intergenerational_trauma_support"],
                    "france": ["midlife_career_transitions", "social_security_optimization"]
                }
            },
            "senior": {
                "most_effective": ["medical_social_work", "senior_centers", "home_services", "family_support"],
                "considerations": ["Physical health priority", "Social isolation risk", "Fixed income challenges"],
                "country_specific": {
                    "canada": ["indigenous_elder_care", "winter_wellness_programs"],
                    "united_kingdom": ["nhs_elderly_care", "community_befriending"],
                    "sweden": ["seasonal_depression_support", "active_aging_programs"],
                    "israel": ["holocaust_survivor_support", "veteran_elder_care", "religious_community_integration"],
                    "france": ["social_solidarity_programs", "retirement_home_alternatives",
                               "cultural_activity_integration"]
                }
            }
        }

        # Financial status impact with country context
        self.financial_treatment_map = {
            "low_income": {
                "accessible": ["community_health_centers", "sliding_scale_therapy", "support_groups",
                               "crisis_hotlines"],
                "barriers": ["Limited transportation", "Work schedule conflicts", "Childcare needs"],
                "country_resources": {
                    "united_states": ["medicaid", "community_health_centers", "211_services"],
                    "canada": ["provincial_health_services", "community_mental_health"],
                    "united_kingdom": ["nhs_services", "local_authority_support"],
                    "australia": ["bulk_billing_gps", "community_health_services"],
                    "germany": ["statutory_insurance_coverage", "social_services"],
                    "india": ["government_health_schemes", "ngos", "community_workers"],
                    "brazil": ["sus_services", "community_health_agents"],
                    "south_africa": ["public_health_facilities", "community_organizations"],
                    "sweden": ["regional_health_services", "municipal_support"],
                    "japan": ["national_health_insurance", "municipal_services"],
                    "israel": ["kupat_cholim_services", "municipal_welfare_departments", "nonprofit_organizations"],
                    "france": ["cpam_coverage", "municipal_social_services", "associations_support"]
                }
            },
            "moderate_income": {
                "accessible": ["employer_eap", "insurance_covered_therapy", "community_programs", "online_therapy"],
                "barriers": ["Insurance copays", "Time constraints", "Stigma concerns"],
                "country_resources": {
                    "united_states": ["employer_insurance", "health_savings_accounts"],
                    "canada": ["extended_health_benefits", "provincial_programs"],
                    "united_kingdom": ["private_healthcare_options", "nhs_plus_private"],
                    "australia": ["medicare_plus_private", "mental_health_plans"],
                    "germany": ["statutory_plus_private_insurance"],
                    "sweden": ["regional_healthcare", "private_supplements"],
                    "israel": ["health_fund_coverage", "supplementary_insurance"],
                    "france": ["secu_plus_mutuelle", "professional_health_coverage"]
                }
            },
            "stable_income": {
                "accessible": ["private_therapy", "specialized_treatment", "wellness_programs", "preventive_care"],
                "barriers": ["Finding quality providers", "Time management"],
                "country_resources": {
                    "united_states": ["private_practice", "concierge_medicine"],
                    "united_kingdom": ["private_healthcare", "bupa_services"],
                    "australia": ["private_health_insurance", "specialist_care"],
                    "germany": ["private_insurance_options", "specialist_clinics"],
                    "israel": ["private_health_services", "premium_health_funds"],
                    "france": ["private_practice_options", "premium_mutuelle_coverage"]
                }
            }
        }


class GlobalSocialWorkerChatbot:
    def __init__(self):
        self.current_patient = None
        self.session_active = False
        self.health_db = GlobalHealthDatabase()

    def start_session(self):
        """Initialize a new patient session"""
        print("=" * 80)
        print("GLOBAL SOCIAL WORKER ASSISTANT CHATBOT")
        print("Country-Specific Patient Assessment & Evidence-Based Recommendations")
        print("=" * 80)
        self.session_active = True

    def get_country_list(self) -> Dict[str, str]:
        """Return available countries with display names"""
        return {
            "1": ("united_states", "United States"),
            "2": ("canada", "Canada"),
            "3": ("united_kingdom", "United Kingdom"),
            "4": ("australia", "Australia"),
            "5": ("germany", "Germany"),
            "6": ("japan", "Japan"),
            "7": ("india", "India"),
            "8": ("brazil", "Brazil"),
            "9": ("south_africa", "South Africa"),
            "10": ("sweden", "Sweden"),
            "11": ("israel", "Israel"),
            "12": ("france", "France")
        }

    def determine_age_category(self, age: int) -> str:
        """Categorize age for treatment recommendations"""
        if 18 <= age <= 25:
            return "young_adult"
        elif 26 <= age <= 45:
            return "adult"
        elif 46 <= age <= 64:
            return "middle_aged"
        else:
            return "senior"

    def determine_city_category(self, city: str, country: str) -> str:
        """Categorize city size with country context"""
        city_lower = city.lower().strip()

        # Country-specific major cities
        major_cities_by_country = {
            "united_states": ["new york", "los angeles", "chicago", "houston", "phoenix", "philadelphia",
                              "san antonio", "san diego", "dallas", "san jose", "austin", "jacksonville"],
            "canada": ["toronto", "montreal", "vancouver", "calgary", "edmonton", "ottawa", "winnipeg"],
            "united_kingdom": ["london", "birmingham", "manchester", "glasgow", "liverpool", "leeds", "sheffield"],
            "australia": ["sydney", "melbourne", "brisbane", "perth", "adelaide", "gold coast", "canberra"],
            "germany": ["berlin", "hamburg", "munich", "cologne", "frankfurt", "stuttgart", "düsseldorf"],
            "japan": ["tokyo", "osaka", "yokohama", "nagoya", "sapporo", "fukuoka", "kyoto"],
            "india": ["mumbai", "delhi", "bangalore", "kolkata", "chennai", "hyderabad", "pune"],
            "brazil": ["são paulo", "rio de janeiro", "brasília", "salvador", "fortaleza", "belo horizonte"],
            "south_africa": ["johannesburg", "cape town", "durban", "pretoria", "port elizabeth"],
            "sweden": ["stockholm", "göteborg", "malmö", "uppsala", "västerås", "örebro"],
            "israel": ["tel aviv", "jerusalem", "haifa", "rishon lezion", "petah tikva", "ashdod", "netanya"],
            "france": ["paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg", "montpellier"]
        }

        if country in major_cities_by_country:
            for major_city in major_cities_by_country[country]:
                if major_city in city_lower:
                    return "major_city"

        # Rural indicators
        if any(keyword in city_lower for keyword in ["county", "township", "village", "rural", "farm"]):
            return "rural"

        return "suburban"

    def collect_patient_info(self) -> PatientProfile:
        """Collect comprehensive patient information including country"""
        print("\n--- Global Patient Assessment ---")

        # Basic information
        name = input("Patient's name (or initials for privacy): ").strip()

        # Age collection with validation
        while True:
            try:
                age = int(input("Patient's age: "))
                if 0 <= age <= 120:
                    break
                else:
                    print("Please enter a valid age (0-120)")
            except ValueError:
                print("Please enter a valid number for age")

        # Country selection
        print("\nCountry options:")
        country_options = self.get_country_list()
        for key, (code, display_name) in country_options.items():
            print(f"{key}. {display_name}")

        while True:
            country_choice = input("Select country (1-12): ").strip()
            if country_choice in country_options:
                country_code, country_display = country_options[country_choice]
                break
            print("Please enter a valid option (1-12)")

        # City information
        city = input(f"Patient's city/location in {country_display}: ").strip()

        # Gender selection
        print("\nGender options:")
        print("1. Male")
        print("2. Female")
        print("3. Non-binary")
        print("4. Prefer not to say")
        while True:
            gender_choice = input("Select gender (1-4): ").strip()
            gender_map = {"1": "Male", "2": "Female", "3": "Non-binary", "4": "Prefer not to say"}
            if gender_choice in gender_map:
                gender = gender_map[gender_choice]
                break
            print("Please enter a valid option (1-4)")

        # Employment status
        print("\nEmployment status options:")
        print("1. Full-time employed")
        print("2. Part-time employed")
        print("3. Unemployed - actively seeking")
        print("4. Unemployed - not seeking")
        print("5. Student")
        print("6. Retired")
        print("7. Unable to work")
        while True:
            emp_choice = input("Select employment status (1-7): ").strip()
            emp_map = {
                "1": "Full-time employed",
                "2": "Part-time employed",
                "3": "Unemployed - actively seeking",
                "4": "Unemployed - not seeking",
                "5": "Student",
                "6": "Retired",
                "7": "Unable to work"
            }
            if emp_choice in emp_map:
                employment_status = emp_map[emp_choice]
                break
            print("Please enter a valid option (1-7)")

        # Financial status (context-aware by country)
        print(f"\nFinancial status options (relative to {country_display} standards):")
        print("1. Low income - difficulty meeting basic needs")
        print("2. Moderate income - meets basic needs with some constraints")
        print("3. Stable income - comfortable with discretionary spending")
        while True:
            fin_choice = input("Select financial status (1-3): ").strip()
            fin_map = {
                "1": "low_income",
                "2": "moderate_income",
                "3": "stable_income"
            }
            if fin_choice in fin_map:
                financial_status = fin_map[fin_choice]
                break
            print("Please enter a valid option (1-3)")

        # Exercise level
        print("\nExercise level options:")
        print("1. Very active (5+ times per week)")
        print("2. Moderately active (3-4 times per week)")
        print("3. Lightly active (1-2 times per week)")
        print("4. Sedentary (little to no exercise)")
        while True:
            exercise_choice = input("Select exercise level (1-4): ").strip()
            exercise_map = {
                "1": "Very active",
                "2": "Moderately active",
                "3": "Lightly active",
                "4": "Sedentary"
            }
            if exercise_choice in exercise_map:
                exercise_level = exercise_map[exercise_choice]
                break
            print("Please enter a valid option (1-4)")

        # Mental state assessment
        print("\nMental state assessment:")
        print("1. Excellent - feeling very positive and energetic")
        print("2. Good - generally positive with minor concerns")
        print("3. Fair - some challenges but managing")
        print("4. Poor - struggling with daily activities")
        print("5. Critical - severe distress or crisis")
        while True:
            mental_choice = input("Select mental state (1-5): ").strip()
            mental_map = {
                "1": "Excellent",
                "2": "Good",
                "3": "Fair",
                "4": "Poor",
                "5": "Critical"
            }
            if mental_choice in mental_map:
                mental_state = mental_map[mental_choice]
                break
            print("Please enter a valid option (1-5)")

        # Additional notes
        additional_notes = input("\nAny additional notes or concerns (optional): ").strip()

        return PatientProfile(
            name=name,
            age=age,
            country=country_code,
            city=city,
            gender=gender,
            employment_status=employment_status,
            exercise_level=exercise_level,
            mental_state=mental_state,
            financial_status=financial_status,
            additional_notes=additional_notes
        )

    def assess_country_specific_health_needs(self, patient: PatientProfile) -> Dict[str, List[str]]:
        """Assess health needs based on country-specific health statistics"""
        health_needs = {
            "country_priority_health_issues": [],
            "preventive_care_country_specific": [],
            "mental_health_cultural_considerations": [],
            "healthcare_system_navigation": []
        }

        country_data = self.health_db.country_health_data.get(patient.country, {})
        age_category = self.determine_age_category(patient.age)

        # Country-specific common health issues
        common_issues = country_data.get("common_health_issues", [])
        health_needs["country_priority_health_issues"] = [
            f"Screen for {issue.replace('_', ' ')}" for issue in common_issues[:3]
        ]

        # Mental health prevalence context
        mental_prevalence = country_data.get("mental_health_prevalence", 0.20)
        if patient.mental_state in ["Poor", "Critical"]:
            health_needs["mental_health_cultural_considerations"].append(
                f"Mental health affects {mental_prevalence * 100:.0f}% of population in {patient.country.replace('_', ' ').title()}"
            )

        # Cultural considerations
        cultural_factors = country_data.get("cultural_considerations", [])
        for factor in cultural_factors:
            if factor == "mental_health_stigma" and patient.mental_state in ["Fair", "Poor", "Critical"]:
                health_needs["mental_health_cultural_considerations"].append(
                    "Address cultural stigma around mental health treatment"
                )
            elif factor == "family_centered_care":
                health_needs["mental_health_cultural_considerations"].append(
                    "Include family in treatment planning when appropriate"
                )
            elif factor == "work_stress" and "employed" in patient.employment_status.lower():
                health_needs["mental_health_cultural_considerations"].append(
                    "Address work-related stress common in this cultural context"
                )

        # Healthcare system navigation
        healthcare_system = country_data.get("healthcare_system", "")
        if healthcare_system == "private_insurance":
            health_needs["healthcare_system_navigation"].append(
                "Assist with insurance navigation and coverage verification"
            )
        elif healthcare_system == "universal_healthcare":
            health_needs["healthcare_system_navigation"].append(
                "Connect with publicly funded health services"
            )
        elif healthcare_system == "mixed_public_private":
            health_needs["healthcare_system_navigation"].append(
                "Evaluate best public vs. private options based on needs and finances"
            )

        # Preventive care focus
        preventive_focus = country_data.get("preventive_care_focus", [])
        health_needs["preventive_care_country_specific"] = [
            focus.replace('_', ' ').title() for focus in preventive_focus
        ]

        return health_needs

    def assess_country_specific_safety_needs(self, patient: PatientProfile) -> Dict[str, List[str]]:
        """Assess safety needs with country-specific context"""
        safety_needs = {
            "crisis_resources_local": [],
            "cultural_safety_considerations": [],
            "country_specific_risks": [],
            "social_support_systems": []
        }

        country_data = self.health_db.country_health_data.get(patient.country, {})

        # Crisis resources
        crisis_resources = country_data.get("crisis_resources", [])
        if patient.mental_state in ["Critical", "Poor"]:
            safety_needs["crisis_resources_local"] = [
                f"Emergency: {resource}" for resource in crisis_resources
            ]

        # Country-specific risk factors
        common_issues = country_data.get("common_health_issues", [])
        if "violence_related_trauma" in common_issues:
            safety_needs["country_specific_risks"].append(
                "Violence-related trauma screening and safety planning"
            )
        if "suicide_risk" in common_issues:
            safety_needs["country_specific_risks"].append(
                "Elevated suicide risk awareness and prevention"
            )

        # Cultural safety considerations
        cultural_factors = country_data.get("cultural_considerations", [])
        if "indigenous_health_needs" in cultural_factors:
            safety_needs["cultural_safety_considerations"].append(
                "Consider indigenous cultural safety and traditional healing"
            )
        if "socioeconomic_disparities" in cultural_factors:
            safety_needs["cultural_safety_considerations"].append(
                "Address socioeconomic safety concerns and resource access"
            )

        return safety_needs

    def generate_country_evidence_recommendations(self, patient: PatientProfile) -> Dict[str, List[str]]:
        """Generate evidence-based recommendations using country-specific data"""
        recommendations = {
            "Country-Specific Treatment Options": [],
            "Healthcare System Navigation": [],
            "Cultural Treatment Adaptations": [],
            "Financial Access Strategies": []
        }

        age_category = self.determine_age_category(patient.age)
        country_data = self.health_db.country_health_data.get(patient.country, {})

        # Age and country-specific treatments
        age_treatments = self.health_db.age_based_treatments[age_category]
        country_specific = age_treatments.get("country_specific", {}).get(patient.country, [])

        if country_specific:
            recommendations["Country-Specific Treatment Options"].extend([
                f"Recommended for {age_category} in {patient.country.replace('_', ' ').title()}: {', '.join(country_specific)}"
            ])

        # Financial access by country
        financial_resources = self.health_db.financial_treatment_map[patient.financial_status].get("country_resources",
                                                                                                   {})
        country_financial_resources = financial_resources.get(patient.country, [])

        if country_financial_resources:
            recommendations["Financial Access Strategies"] = [
                f"Available in {patient.country.replace('_', ' ').title()}: {', '.join(country_financial_resources)}"
            ]

        # Healthcare system specific guidance
        healthcare_system = country_data.get("healthcare_system", "")
        treatment_access = country_data.get("treatment_accessibility", "")

        if healthcare_system == "universal_healthcare":
            recommendations["Healthcare System Navigation"].append(
                "Utilize publicly funded mental health services with no direct cost"
            )
        elif healthcare_system == "private_insurance":
            recommendations["Healthcare System Navigation"].append(
                "Verify insurance coverage and seek in-network providers"
            )
        elif healthcare_system == "nhs":
            recommendations["Healthcare System Navigation"].append(
                "Access NHS mental health services through GP referral or self-referral"
            )

        # Cultural adaptations
        cultural_factors = country_data.get("cultural_considerations", [])
        if "traditional_medicine" in cultural_factors:
            recommendations["Cultural Treatment Adaptations"].append(
                "Consider integration of traditional healing practices with modern treatment"
            )
        if "family_centered_care" in cultural_factors:
            recommendations["Cultural Treatment Adaptations"].append(
                "Adapt treatment to include family involvement and collective decision-making"
            )

        return recommendations

    def display_global_assessment(self, patient: PatientProfile, country_health: Dict,
                                  country_safety: Dict, country_evidence: Dict, general_recs: Dict):
        """Display comprehensive global assessment results"""
        print("\n" + "=" * 90)
        print(f"GLOBAL CARE ASSESSMENT FOR {patient.name.upper()}")
        print(f"Country: {patient.country.replace('_', ' ').title()}")
        print(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')}")
        print("=" * 90)

        # Patient profile with country context
        country_data = self.health_db.country_health_data.get(patient.country, {})
        mental_prevalence = country_data.get("mental_health_prevalence", 0.20)

        print(f"\nPATIENT PROFILE:")
        print(f"• Name: {patient.name}")
        print(f"• Age: {patient.age} ({self.determine_age_category(patient.age).replace('_', ' ').title()})")
        print(f"• Country: {patient.country.replace('_', ' ').title()}")
        print(
            f"• City: {patient.city} ({self.determine_city_category(patient.city, patient.country).replace('_', ' ').title()})")
        print(f"• Gender: {patient.gender}")
        print(f"• Employment: {patient.employment_status}")
        print(f"• Financial Status: {patient.financial_status.replace('_', ' ').title()}")
        print(f"• Exercise Level: {patient.exercise_level}")
        print(f"• Mental State: {patient.mental_state}")
        if patient.additional_notes:
            print(f"• Additional Notes: {patient.additional_notes}")

        print(f"\n🌍 COUNTRY HEALTH CONTEXT:")
        print(
            f"• Mental health prevalence in {patient.country.replace('_', ' ').title()}: {mental_prevalence * 100:.0f}%")
        print(f"• Healthcare system: {country_data.get('healthcare_system', 'Unknown').replace('_', ' ').title()}")
        print(f"• Common health issues: {', '.join(country_data.get('common_health_issues', [])[:3])}")

        # Country-specific health needs
        print(f"\n🏥 COUNTRY-SPECIFIC HEALTH ASSESSMENT:")
        print("-" * 60)
        for category, needs in country_health.items():
            if needs:
                print(f"\n{category.replace('_', ' ').title()}:")
                for need in needs:
                    print(f"  • {need}")

        # Country-specific safety needs
        print(f"\n🛡️ CULTURAL SAFETY ASSESSMENT:")
        print("-" * 60)
        for category, needs in country_safety.items():
            if needs:
                print(f"\n{category.replace('_', ' ').title()}:")
                for need in needs:
                    print(f"  • {need}")

        # Country evidence-based recommendations
        print(f"\n📊 COUNTRY-SPECIFIC EVIDENCE-BASED RECOMMENDATIONS:")
        print("-" * 60)
        for category, recs in country_evidence.items():
            if recs:
                print(f"\n{category}:")
                for rec in recs:
                    print(f"  • {rec}")

        # General weekly recommendations
        print(f"\n📋 WEEKLY ACTION PLAN:")
        print("-" * 60)
        for category, recs in general_recs.items():
            if recs:
                print(f"\n{category}:")
                for i, rec in enumerate(recs, 1):
                    print(f"  {i}. {rec}")

        # Country-specific crisis resources
        crisis_resources = country_data.get("crisis_resources", [])
        print("\n" + "=" * 90)
        print("⚠️ EMERGENCY RESOURCES:")
        if crisis_resources:
            print(
                f"• Emergency contacts for {patient.country.replace('_', ' ').title()}: {', '.join(crisis_resources)}")
        print("• These recommendations consider country-specific health statistics and cultural factors")
        print("• Consult local healthcare professionals familiar with national health systems")
        print("• Cultural adaptation of treatment approaches is recommended")
        print("=" * 90)

    def generate_comprehensive_recommendations(self, patient: PatientProfile) -> Dict[str, List[str]]:
        """Generate comprehensive recommendations including country-specific factors"""
        recommendations = {
            "Physical Health": [],
            "Mental Health": [],
            "Social/Professional": [],
            "Daily Structure": [],
            "Crisis Support": []
        }

        country_data = self.health_db.country_health_data.get(patient.country, {})
        common_issues = country_data.get("common_health_issues", [])
        age_category = self.determine_age_category(patient.age)

        # Physical health recommendations with country context
        if patient.exercise_level == "Sedentary":
            if "obesity" in common_issues:
                recommendations["Physical Health"].append(
                    f"Address obesity prevention - priority health issue in {patient.country.replace('_', ' ').title()}"
                )
            if patient.country == "australia" and "skin_cancer" in common_issues:
                recommendations["Physical Health"].append("Sun-safe exercise options due to high skin cancer rates")
            elif patient.country == "sweden":
                recommendations["Physical Health"].append("Indoor exercise options for seasonal depression prevention")

            if patient.financial_status == "low_income":
                recommendations["Physical Health"].extend([
                    "Free community walking groups",
                    "Public park exercise facilities",
                    "Community center programs"
                ])
            else:
                recommendations["Physical Health"].extend([
                    "Start with 10-15 minutes of daily walking",
                    "Consider local fitness facilities"
                ])

        # Mental health with country-specific considerations
        if patient.mental_state in ["Critical", "Poor"]:
            crisis_resources = country_data.get("crisis_resources", [])
            if crisis_resources:
                recommendations["Crisis Support"].extend([
                    f"Contact crisis services: {', '.join(crisis_resources)}",
                    "Immediate safety planning with local cultural considerations"
                ])

            # Country-specific mental health approaches
            if patient.country == "japan" and "mental_health_stigma" in country_data.get("cultural_considerations", []):
                recommendations["Mental Health"].append(
                    "Consider culturally-sensitive mental health services that address stigma")
            elif patient.country == "india" and "family_centered_care" in country_data.get("cultural_considerations",
                                                                                           []):
                recommendations["Mental Health"].append("Family therapy integration with cultural values")
            elif patient.country == "south_africa" and "ubuntu_philosophy" in country_data.get(
                    "cultural_considerations", []):
                recommendations["Mental Health"].append(
                    "Community-based healing approaches aligned with Ubuntu philosophy")

        # Employment and social recommendations by country
        if "unemployed" in patient.employment_status.lower():
            if patient.country == "germany":
                recommendations["Social/Professional"].append(
                    "Access Federal Employment Agency (Bundesagentur für Arbeit) services")
            elif patient.country == "canada":
                recommendations["Social/Professional"].append("Utilize Employment Insurance and job training programs")
            elif patient.country == "united_kingdom":
                recommendations["Social/Professional"].append("Access Jobcentre Plus and Universal Credit support")
            elif patient.country == "australia":
                recommendations["Social/Professional"].append("Contact Centrelink for employment services and support")
            elif patient.country == "sweden":
                recommendations["Social/Professional"].append(
                    "Register with Arbetsförmedlingen (Swedish Public Employment Service)")

        # Country-specific daily structure recommendations
        if patient.country == "sweden" and age_category in ["adult", "middle_aged"]:
            recommendations["Daily Structure"].append("Light therapy routine during dark winter months")
        elif patient.country == "japan" and "employed" in patient.employment_status.lower():
            recommendations["Daily Structure"].append("Work-life balance practices to prevent karoshi (overwork)")
        elif patient.country == "brazil" and "family_support" in country_data.get("cultural_considerations", []):
            recommendations["Daily Structure"].append("Include family meal times and community connections")

        return recommendations

    def save_global_assessment(self, patient: PatientProfile, country_health: Dict,
                               country_safety: Dict, country_evidence: Dict, general_recs: Dict):
        """Save comprehensive global assessment to file"""
        filename = f"global_assessment_{patient.name.replace(' ', '_')}_{patient.country}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"GLOBAL CARE ASSESSMENT FOR {patient.name.upper()}\n")
                f.write(f"Country: {patient.country.replace('_', ' ').title()}\n")
                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')}\n")
                f.write("=" * 90 + "\n\n")

                # Patient profile
                country_data = self.health_db.country_health_data.get(patient.country, {})
                mental_prevalence = country_data.get("mental_health_prevalence", 0.20)

                f.write("PATIENT PROFILE:\n")
                f.write(f"• Name: {patient.name}\n")
                f.write(
                    f"• Age: {patient.age} ({self.determine_age_category(patient.age).replace('_', ' ').title()})\n")
                f.write(f"• Country: {patient.country.replace('_', ' ').title()}\n")
                f.write(
                    f"• City: {patient.city} ({self.determine_city_category(patient.city, patient.country).replace('_', ' ').title()})\n")
                f.write(f"• Gender: {patient.gender}\n")
                f.write(f"• Employment: {patient.employment_status}\n")
                f.write(f"• Financial Status: {patient.financial_status.replace('_', ' ').title()}\n")
                f.write(f"• Exercise Level: {patient.exercise_level}\n")
                f.write(f"• Mental State: {patient.mental_state}\n")
                if patient.additional_notes:
                    f.write(f"• Additional Notes: {patient.additional_notes}\n")

                f.write(f"\nCOUNTRY HEALTH CONTEXT:\n")
                f.write(
                    f"• Mental health prevalence in {patient.country.replace('_', ' ').title()}: {mental_prevalence * 100:.0f}%\n")
                f.write(
                    f"• Healthcare system: {country_data.get('healthcare_system', 'Unknown').replace('_', ' ').title()}\n")
                f.write(f"• Common health issues: {', '.join(country_data.get('common_health_issues', [])[:3])}\n")

                # Write all assessment sections
                sections = [
                    ("COUNTRY-SPECIFIC HEALTH ASSESSMENT", country_health),
                    ("CULTURAL SAFETY ASSESSMENT", country_safety),
                    ("COUNTRY-SPECIFIC EVIDENCE-BASED RECOMMENDATIONS", country_evidence),
                    ("WEEKLY ACTION PLAN", general_recs)
                ]

                for section_title, section_data in sections:
                    f.write(f"\n{section_title}:\n")
                    f.write("-" * 60 + "\n")
                    for category, items in section_data.items():
                        if items:
                            f.write(f"\n{category.replace('_', ' ').title()}:\n")
                            for item in items:
                                f.write(f"  • {item}\n")

                # Crisis resources
                crisis_resources = country_data.get("crisis_resources", [])
                f.write("\n" + "=" * 90 + "\n")
                f.write("EMERGENCY RESOURCES:\n")
                if crisis_resources:
                    f.write(
                        f"• Emergency contacts for {patient.country.replace('_', ' ').title()}: {', '.join(crisis_resources)}\n")
                f.write("• These recommendations consider country-specific health statistics and cultural factors\n")
                f.write("• Consult local healthcare professionals familiar with national health systems\n")
                f.write("• Cultural adaptation of treatment approaches is recommended\n")

            print(f"\n✓ Global assessment saved to: {filename}")

        except Exception as e:
            print(f"\n⚠ Could not save file: {e}")

    def run_global_assessment(self):
        """Main function to run the complete global assessment"""
        if not self.session_active:
            self.start_session()

        try:
            # Collect comprehensive patient information including country
            patient = self.collect_patient_info()
            self.current_patient = patient

            print(
                f"\n🔄 Analyzing patient profile with {patient.country.replace('_', ' ').title()} health statistics...")

            # Generate country-specific assessments
            country_health_needs = self.assess_country_specific_health_needs(patient)
            country_safety_needs = self.assess_country_specific_safety_needs(patient)
            country_evidence_recs = self.generate_country_evidence_recommendations(patient)
            general_recommendations = self.generate_comprehensive_recommendations(patient)

            # Display comprehensive results
            self.display_global_assessment(
                patient, country_health_needs, country_safety_needs,
                country_evidence_recs, general_recommendations
            )

            # Ask about saving
            save_choice = input("\nWould you like to save this global assessment to a file? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                self.save_global_assessment(
                    patient, country_health_needs, country_safety_needs,
                    country_evidence_recs, general_recommendations
                )

            # Ask about new assessment
            continue_choice = input("\nWould you like to assess another patient? (y/n): ").strip().lower()
            if continue_choice in ['y', 'yes']:
                self.run_global_assessment()
            else:
                print("\nThank you for using the Global Social Worker Assistant Chatbot!")
                print("Remember: Always consider cultural context and local healthcare systems.")
                self.session_active = False

        except KeyboardInterrupt:
            print("\n\nSession ended by user. Goodbye!")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please restart the assessment.")


# Example usage and main execution
if __name__ == "__main__":
    # Create and run the global chatbot
    chatbot = GlobalSocialWorkerChatbot()
    chatbot.run_global_assessment()