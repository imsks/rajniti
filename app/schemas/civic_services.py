"""
Taxonomy for the Citizens' Awareness module (government app/service finder).

The tags are a fixed enum (not freeform) so that multiple contributors tag the
curated dataset in `app/data/civic_services.json` consistently.
"""

from enum import Enum as _Enum
from typing import Any, Dict, List


class ProblemDomain(str, _Enum):
    """What problem is the citizen facing?"""

    RTI = "rti"
    PUBLIC_GRIEVANCE = "public-grievance"
    CORRUPTION = "corruption"
    CIVIC_COMPLAINT = "civic-complaint"
    CONSUMER_GRIEVANCE = "consumer-grievance"
    CYBERCRIME = "cybercrime"
    WOMEN_CHILD_SAFETY = "women-child-safety"
    EMERGENCY = "emergency"
    DOCUMENTS = "documents"
    LAND_RECORDS = "land-records"
    PENSION_WELFARE = "pension-welfare"
    VOTER_SERVICES = "voter-services"
    HEALTH = "health"
    EDUCATION_SCHOLARSHIP = "education-scholarship"
    FARMER_AGRICULTURE = "farmer-agriculture"
    LABOUR_EMPLOYMENT = "labour-employment"
    TAX_FINANCE = "tax-finance"
    TRANSPORT_VEHICLE = "transport-vehicle"


class Platform(str, _Enum):
    """Where the service can be used."""

    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    HELPLINE = "helpline"
    SMS = "sms"


class Jurisdiction(str, _Enum):
    """Who runs the service."""

    CENTRAL = "central"
    STATE = "state"


# Guided flow: "What problem are you facing?" — one entry per problem domain.
# `prompt` is written in the citizen's own words, not in government vocabulary.
GUIDED_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": ProblemDomain.RTI.value,
        "label": "Right to Information",
        "prompt": "I want information the government is not sharing",
    },
    {
        "id": ProblemDomain.PUBLIC_GRIEVANCE.value,
        "label": "Public grievance",
        "prompt": "A government office is not doing its job",
    },
    {
        "id": ProblemDomain.CORRUPTION.value,
        "label": "Corruption",
        "prompt": "Someone is asking me for a bribe",
    },
    {
        "id": ProblemDomain.CIVIC_COMPLAINT.value,
        "label": "Civic complaint",
        "prompt": "My street has potholes, garbage, no water or no streetlight",
    },
    {
        "id": ProblemDomain.CONSUMER_GRIEVANCE.value,
        "label": "Consumer complaint",
        "prompt": "A company cheated me or will not refund my money",
    },
    {
        "id": ProblemDomain.CYBERCRIME.value,
        "label": "Cybercrime",
        "prompt": "I lost money to an online fraud or someone is harassing me online",
    },
    {
        "id": ProblemDomain.WOMEN_CHILD_SAFETY.value,
        "label": "Women and child safety",
        "prompt": "A woman or a child needs help or is in danger",
    },
    {
        "id": ProblemDomain.EMERGENCY.value,
        "label": "Emergency",
        "prompt": "I need police, ambulance or fire help right now",
    },
    {
        "id": ProblemDomain.DOCUMENTS.value,
        "label": "Documents and identity",
        "prompt": "I need my Aadhaar, PAN, certificates or other documents",
    },
    {
        "id": ProblemDomain.LAND_RECORDS.value,
        "label": "Land and property",
        "prompt": "I need land records, mutation or property papers",
    },
    {
        "id": ProblemDomain.PENSION_WELFARE.value,
        "label": "Pension and welfare",
        "prompt": "My pension, ration or welfare scheme money is not reaching me",
    },
    {
        "id": ProblemDomain.VOTER_SERVICES.value,
        "label": "Voter services",
        "prompt": "I need a voter ID, or want to check or correct my voter details",
    },
    {
        "id": ProblemDomain.HEALTH.value,
        "label": "Health",
        "prompt": "I need treatment, health insurance or medicines",
    },
    {
        "id": ProblemDomain.EDUCATION_SCHOLARSHIP.value,
        "label": "Education and scholarships",
        "prompt": "I need a scholarship or help with school and college",
    },
    {
        "id": ProblemDomain.FARMER_AGRICULTURE.value,
        "label": "Farming",
        "prompt": "I am a farmer and need scheme money, crop insurance or prices",
    },
    {
        "id": ProblemDomain.LABOUR_EMPLOYMENT.value,
        "label": "Work and wages",
        "prompt": "My wages, PF or job rights are being denied",
    },
    {
        "id": ProblemDomain.TAX_FINANCE.value,
        "label": "Tax and money",
        "prompt": "I need help with income tax, refunds or a bank complaint",
    },
    {
        "id": ProblemDomain.TRANSPORT_VEHICLE.value,
        "label": "Vehicles and transport",
        "prompt": "I need my driving licence, RC or want to pay a traffic challan",
    },
]

PROBLEM_DOMAINS: List[str] = [d.value for d in ProblemDomain]
PLATFORMS: List[str] = [p.value for p in Platform]
JURISDICTIONS: List[str] = [j.value for j in Jurisdiction]
