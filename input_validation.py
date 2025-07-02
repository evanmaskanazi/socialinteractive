import re
import datetime
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Union


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    value: Optional[Union[str, int]]
    error_message: str = ""
    suggestions: List[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class GlobalInputValidator:
    """Comprehensive input validation system for the Global Social Worker Chatbot"""

    def __init__(self):
        self.country_options = {
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

        # Common city names by country for validation assistance
        self.major_cities_by_country = {
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

    def validate_name(self, name: str) -> ValidationResult:
        """Validate patient name or initials"""
        name = name.strip()

        if not name:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Name cannot be empty",
                suggestions=["Enter patient's full name or initials for privacy (e.g., 'J.D.' or 'John Doe')"]
            )

        if len(name) > 100:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Name is too long (maximum 100 characters)",
                suggestions=["Use initials or shorter name format"]
            )

        # Check for potentially invalid characters
        if re.search(r'[<>{}[\]\\|`~!@#$%^&*()+=]', name):
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Name contains invalid characters",
                suggestions=["Use only letters, spaces, periods, hyphens, and apostrophes"]
            )

        # Check for reasonable name pattern
        if re.match(r'^[A-Za-z\s\.\-\']+$', name):
            return ValidationResult(is_valid=True, value=name)

        return ValidationResult(
            is_valid=False,
            value=None,
            error_message="Invalid name format",
            suggestions=["Use letters, spaces, periods (for initials), hyphens, or apostrophes only"]
        )

    def validate_age(self, age_input: str) -> ValidationResult:
        """Validate patient age"""
        age_input = age_input.strip()

        if not age_input:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Age cannot be empty",
                suggestions=["Enter a number between 0 and 120"]
            )

        try:
            age = int(age_input)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Age must be a valid number",
                suggestions=["Enter a whole number (e.g., 25, 45, 67)"]
            )

        if age < 0:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Age cannot be negative",
                suggestions=["Enter a positive number"]
            )

        if age > 120:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Age cannot exceed 120 years",
                suggestions=["Please verify the age is correct"]
            )

        if age < 18:
            return ValidationResult(
                is_valid=True,
                value=age,
                suggestions=["Note: Patient is a minor - consider guardian consent and specialized protocols"]
            )

        return ValidationResult(is_valid=True, value=age)

    def validate_country_selection(self, country_input: str) -> ValidationResult:
        """Validate country selection"""
        country_input = country_input.strip()

        if not country_input:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Country selection cannot be empty",
                suggestions=[f"Enter a number from 1-{len(self.country_options)}"]
            )

        if country_input not in self.country_options:
            # Try to match by country name
            country_input_lower = country_input.lower()
            for key, (code, display_name) in self.country_options.items():
                if (country_input_lower in display_name.lower() or
                        country_input_lower in code.lower()):
                    return ValidationResult(
                        is_valid=True,
                        value=key,
                        suggestions=[f"Matched to: {display_name}"]
                    )

            return ValidationResult(
                is_valid=False,
                value=None,
                error_message=f"Invalid country selection: '{country_input}'",
                suggestions=[
                    f"Enter a number from 1-{len(self.country_options)}",
                    "Available options: " + ", ".join([f"{k}={v[1]}" for k, v in self.country_options.items()])
                ]
            )

        country_code, country_name = self.country_options[country_input]
        return ValidationResult(
            is_valid=True,
            value=country_input,
            suggestions=[f"Selected: {country_name}"]
        )

    def validate_city(self, city_input: str, country_code: str = None) -> ValidationResult:
        """Validate city name with country context"""
        city_input = city_input.strip()

        if not city_input:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="City cannot be empty",
                suggestions=["Enter the city or location name"]
            )

        if len(city_input) > 100:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="City name is too long (maximum 100 characters)"
            )

        # Check for valid city name characters
        if not re.match(r'^[A-Za-z\s\.\-\'àáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ]+$', city_input):
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="City name contains invalid characters",
                suggestions=["Use only letters, spaces, periods, hyphens, apostrophes, and accented characters"]
            )

        suggestions = []

        # Provide suggestions if country is known
        if country_code and country_code in self.major_cities_by_country:
            city_lower = city_input.lower()
            major_cities = self.major_cities_by_country[country_code]

            # Check if it's a major city
            for major_city in major_cities:
                if major_city in city_lower or city_lower in major_city:
                    suggestions.append(f"Recognized as major city in {country_code.replace('_', ' ').title()}")
                    break
            else:
                # Suggest similar cities
                similar_cities = [city for city in major_cities if city[0].lower() == city_lower[0].lower()]
                if similar_cities:
                    suggestions.append(
                        f"Similar cities in {country_code.replace('_', ' ').title()}: {', '.join(similar_cities[:3])}")

        return ValidationResult(is_valid=True, value=city_input, suggestions=suggestions)

    def validate_gender_selection(self, gender_input: str) -> ValidationResult:
        """Validate gender selection"""
        gender_input = gender_input.strip()

        gender_map = {
            "1": "Male",
            "2": "Female",
            "3": "Non-binary",
            "4": "Prefer not to say"
        }

        if not gender_input:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Gender selection cannot be empty",
                suggestions=["Enter 1 for Male, 2 for Female, 3 for Non-binary, 4 for Prefer not to say"]
            )

        if gender_input not in gender_map:
            # Try to match by text
            gender_lower = gender_input.lower()
            for key, value in gender_map.items():
                if gender_lower in value.lower() or value.lower().startswith(gender_lower):
                    return ValidationResult(
                        is_valid=True,
                        value=key,
                        suggestions=[f"Matched to: {value}"]
                    )

            return ValidationResult(
                is_valid=False,
                value=None,
                error_message=f"Invalid gender selection: '{gender_input}'",
                suggestions=["Valid options: 1=Male, 2=Female, 3=Non-binary, 4=Prefer not to say"]
            )

        return ValidationResult(
            is_valid=True,
            value=gender_input,
            suggestions=[f"Selected: {gender_map[gender_input]}"]
        )

    def validate_employment_status(self, employment_input: str) -> ValidationResult:
        """Validate employment status selection"""
        employment_input = employment_input.strip()

        employment_map = {
            "1": "Full-time employed",
            "2": "Part-time employed",
            "3": "Unemployed - actively seeking",
            "4": "Unemployed - not seeking",
            "5": "Student",
            "6": "Retired",
            "7": "Unable to work"
        }

        if not employment_input:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Employment status cannot be empty",
                suggestions=["Enter a number from 1-7 for employment status"]
            )

        if employment_input not in employment_map:
            # Try to match by text
            employment_lower = employment_input.lower()
            for key, value in employment_map.items():
                if employment_lower in value.lower():
                    return ValidationResult(
                        is_valid=True,
                        value=key,
                        suggestions=[f"Matched to: {value}"]
                    )

            return ValidationResult(
                is_valid=False,
                value=None,
                error_message=f"Invalid employment status: '{employment_input}'",
                suggestions=[
                    "Valid options:",
                    "1=Full-time employed, 2=Part-time employed, 3=Unemployed (seeking)",
                    "4=Unemployed (not seeking), 5=Student, 6=Retired, 7=Unable to work"
                ]
            )

        return ValidationResult(
            is_valid=True,
            value=employment_input,
            suggestions=[f"Selected: {employment_map[employment_input]}"]
        )

    def validate_financial_status(self, financial_input: str, country_code: str = None) -> ValidationResult:
        """Validate financial status selection with country context"""
        financial_input = financial_input.strip()

        financial_map = {
            "1": "low_income",
            "2": "moderate_income",
            "3": "stable_income"
        }

        if not financial_input:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Financial status cannot be empty",
                suggestions=["Enter 1 for Low income, 2 for Moderate income, 3 for Stable income"]
            )

        if financial_input not in financial_map:
            # Try to match by text
            financial_lower = financial_input.lower()
            text_matches = {
                "low": "1",
                "poor": "1",
                "limited": "1",
                "moderate": "2",
                "middle": "2",
                "average": "2",
                "stable": "3",
                "good": "3",
                "comfortable": "3",
                "high": "3"
            }

            for text, key in text_matches.items():
                if text in financial_lower:
                    return ValidationResult(
                        is_valid=True,
                        value=key,
                        suggestions=[f"Matched to: {financial_map[key].replace('_', ' ').title()}"]
                    )

            return ValidationResult(
                is_valid=False,
                value=None,
                error_message=f"Invalid financial status: '{financial_input}'",
                suggestions=[
                    "Valid options:",
                    "1=Low income (difficulty meeting basic needs)",
                    "2=Moderate income (meets basic needs with constraints)",
                    "3=Stable income (comfortable with discretionary spending)"
                ]
            )

        suggestions = [f"Selected: {financial_map[financial_input].replace('_', ' ').title()}"]

        # Add country-specific context
        if country_code:
            country_name = country_code.replace('_', ' ').title()
            suggestions.append(f"Assessment relative to {country_name} economic standards")

        return ValidationResult(is_valid=True, value=financial_input, suggestions=suggestions)

    def validate_exercise_level(self, exercise_input: str) -> ValidationResult:
        """Validate exercise level selection"""
        exercise_input = exercise_input.strip()

        exercise_map = {
            "1": "Very active",
            "2": "Moderately active",
            "3": "Lightly active",
            "4": "Sedentary"
        }

        if not exercise_input:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message="Exercise level cannot be empty",
                suggestions=["Enter 1-4 for exercise level"]
            )

        if exercise_input not in exercise_map:
            # Try to match by text
            exercise_lower = exercise_input.lower()
            text_matches = {
                "very": "1",
                "high": "1",
                "active": "1",
                "moderate": "2",
                "medium": "2",
                "light": "3",
                "little": "3",
                "sedentary": "4",
                "none": "4",
                "inactive": "4"
            }

            for text, key in text_matches.items():
                if text in exercise_lower:
                    return ValidationResult(
                        is_valid=True,
                        value=key,
                        suggestions=[f"Matched to: {exercise_map[key]}"]
                    )

            return ValidationResult(
                is_valid=False,
                value=None,
                error_message=f"Invalid exercise level: '{exercise_input}'",
                suggestions=[
                    "Valid options:",
                    "1=Very active (5+ times/week), 2=Moderately active (3-4 times/week)",
                    "3=Lightly active (1-2 times/week), 4=Sedentary (little/no exercise)"
                ]
            )

        return ValidationResult(is_valid=True, value=exercise_input,
                                suggestions=[f"Selected: {exercise_map[exercise_input]}"])

    def