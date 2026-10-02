from typing import List
from .data_loader import data_store
from ..models.schemas import EligibilityRequest, EligibilityResponse, SchemeEligibilityMatch

class EligibilityEngine:
    def evaluate(self, request: EligibilityRequest) -> EligibilityResponse:
        matches: List[SchemeEligibilityMatch] = []
        eligible_count = 0

        for scheme in data_store.schemes:
            elig = scheme["eligibility"]
            satisfied = []
            unmet = []

            # 1. Gender check
            if "All" in elig["gender"] or request.gender in elig["gender"]:
                satisfied.append(f"Gender '{request.gender}' meets the requirement ({', '.join(elig['gender'])}).")
            else:
                unmet.append(f"Scheme requires gender: {', '.join(elig['gender'])}; applicant is {request.gender}.")

            # 2. Age check
            if elig["min_age"] <= request.age <= elig["max_age"]:
                satisfied.append(f"Age {request.age} falls within eligible bracket ({elig['min_age']} to {elig['max_age']} years).")
            else:
                unmet.append(f"Age must be between {elig['min_age']} and {elig['max_age']} years (applicant is {request.age}).")

            # 3. Income check
            if elig["max_annual_income"] is None:
                satisfied.append("No maximum income ceiling specified for this universal scheme.")
            elif request.annual_income <= elig["max_annual_income"]:
                satisfied.append(f"Annual income ₹{request.annual_income:,.0f} is within limit (<= ₹{elig['max_annual_income']:,.0f}).")
            else:
                unmet.append(f"Annual income ₹{request.annual_income:,.0f} exceeds maximum allowed limit of ₹{elig['max_annual_income']:,.0f}.")

            # 4. Category check
            if "All" in elig["required_categories"] or request.category in elig["required_categories"]:
                satisfied.append(f"Social category '{request.category}' is eligible.")
            else:
                unmet.append(f"Scheme specifically reserved for categories: {', '.join(elig['required_categories'])}.")

            # 5. Farmer status check
            if elig["farmer_only"]:
                if request.is_farmer:
                    satisfied.append("Applicant holds agricultural land / is a registered farmer in Maharashtra.")
                else:
                    unmet.append("Scheme is strictly reserved for farmers/landowners with 7/12 land records.")

            # 6. Student status check
            if elig["student_only"]:
                if request.is_student:
                    satisfied.append("Applicant is enrolled as a student in approved educational course.")
                else:
                    unmet.append("Scheme is reserved for active students in higher/technical education.")

            # 7. Disability check
            if elig["disability_required"]:
                if request.has_disability:
                    satisfied.append("Applicant has required disability status / UDID certification.")
                else:
                    unmet.append("Scheme requires minimum 40% benchmark disability certification.")

            # Calculate match percentage
            total_checks = len(satisfied) + len(unmet)
            match_percentage = int((len(satisfied) / total_checks) * 100) if total_checks > 0 else 0
            is_eligible = (len(unmet) == 0)

            if is_eligible:
                eligible_count += 1

            matches.append(SchemeEligibilityMatch(
                scheme_id=scheme["id"],
                scheme_name=scheme["name_en"],
                category=scheme["category"],
                financial_benefit=scheme["financial_benefit"],
                eligible=is_eligible,
                match_percentage=match_percentage,
                satisfied_conditions=satisfied,
                unmet_conditions=unmet,
                required_documents=scheme["required_documents"],
                official_portal=scheme["official_portal"],
                source_gr=scheme["source_gr"]
            ))

        # Sort matches by eligible first, then match_percentage descending
        matches.sort(key=lambda x: (x.eligible, x.match_percentage), reverse=True)

        advice = f"Based on your profile, you are eligible for {eligible_count} out of {len(data_store.schemes)} Maharashtra government schemes evaluated. Ensure you have your Aadhaar, Domicile certificate, and Income certificate ready for instant application."

        return EligibilityResponse(
            total_evaluated=len(data_store.schemes),
            eligible_count=eligible_count,
            matches=matches,
            summary_advice=advice
        )

eligibility_engine = EligibilityEngine()
