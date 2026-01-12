"""Vendor auto-categorization service for intelligent vendor classification.

This module provides automatic vendor categorization based on keywords, service types,
and data access patterns. It recommends appropriate risk levels and compliance frameworks
based on the vendor's characteristics.

Based on research of enterprise vendor ecosystems (e.g., DoorDash, enterprise tech stacks).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    """Vendor risk levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VendorCategory(str, Enum):
    """Standard vendor categories for classification."""

    CLOUD_INFRASTRUCTURE = "cloud_infrastructure"
    PAYMENT_FINANCIAL = "payment_financial"
    DATA_ANALYTICS = "data_analytics"
    AI_ML = "ai_ml"
    IDENTITY_ACCESS = "identity_access"
    COMMUNICATION = "communication"
    SECURITY_TOOLS = "security_tools"
    HR_CORPORATE = "hr_corporate"
    MARKETING = "marketing"
    LOGISTICS = "logistics"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    DEVELOPMENT_TOOLS = "development_tools"
    CUSTOMER_SUPPORT = "customer_support"
    OTHER = "other"


@dataclass
class CategoryDefinition:
    """Definition of a vendor category with classification rules."""

    category: VendorCategory
    display_name: str
    description: str
    keywords: list[str]
    risk_level: RiskLevel
    default_frameworks: list[str]
    data_types: list[str]


# Vendor category definitions with classification rules
CATEGORY_DEFINITIONS: dict[VendorCategory, CategoryDefinition] = {
    VendorCategory.CLOUD_INFRASTRUCTURE: CategoryDefinition(
        category=VendorCategory.CLOUD_INFRASTRUCTURE,
        display_name="Cloud Infrastructure",
        description="Cloud hosting, compute, storage, and infrastructure services",
        keywords=[
            "aws",
            "amazon web services",
            "azure",
            "microsoft azure",
            "gcp",
            "google cloud",
            "cloud",
            "hosting",
            "infrastructure",
            "compute",
            "storage",
            "cdn",
            "cloudflare",
            "akamai",
            "fastly",
            "kubernetes",
            "docker",
            "container",
            "serverless",
            "lambda",
            "ec2",
            "s3",
            "iaas",
            "paas",
        ],
        risk_level=RiskLevel.CRITICAL,
        default_frameworks=["soc2", "caiq", "sig_2026", "iso27001"],
        data_types=["production_data", "infrastructure_config", "secrets"],
    ),
    VendorCategory.PAYMENT_FINANCIAL: CategoryDefinition(
        category=VendorCategory.PAYMENT_FINANCIAL,
        display_name="Payment & Financial",
        description="Payment processing, banking, and financial services",
        keywords=[
            "payment",
            "stripe",
            "paypal",
            "braintree",
            "adyen",
            "square",
            "bank",
            "banking",
            "financial",
            "merchant",
            "acquiring",
            "pci",
            "credit card",
            "debit",
            "ach",
            "wire transfer",
            "fintech",
            "billing",
            "invoicing",
            "plaid",
            "chase",
            "wells fargo",
        ],
        risk_level=RiskLevel.CRITICAL,
        default_frameworks=["soc2", "sig_2026", "pci_dss", "dora"],
        data_types=["payment_data", "pii", "financial_records"],
    ),
    VendorCategory.DATA_ANALYTICS: CategoryDefinition(
        category=VendorCategory.DATA_ANALYTICS,
        display_name="Data & Analytics",
        description="Data warehousing, business intelligence, and analytics platforms",
        keywords=[
            "analytics",
            "data warehouse",
            "bi",
            "business intelligence",
            "snowflake",
            "databricks",
            "redshift",
            "bigquery",
            "tableau",
            "looker",
            "power bi",
            "metabase",
            "amplitude",
            "mixpanel",
            "segment",
            "etl",
            "data pipeline",
            "dbt",
            "fivetran",
            "airbyte",
        ],
        risk_level=RiskLevel.HIGH,
        default_frameworks=["soc2", "sig_2026", "iso27001"],
        data_types=["customer_data", "analytics", "aggregated_data"],
    ),
    VendorCategory.AI_ML: CategoryDefinition(
        category=VendorCategory.AI_ML,
        display_name="AI & Machine Learning",
        description="Artificial intelligence, machine learning, and LLM services",
        keywords=[
            "ai",
            "artificial intelligence",
            "ml",
            "machine learning",
            "gpt",
            "llm",
            "large language model",
            "openai",
            "anthropic",
            "claude",
            "google ai",
            "gemini",
            "cohere",
            "hugging face",
            "nlp",
            "natural language",
            "computer vision",
            "deep learning",
            "neural network",
            "model training",
            "inference",
            "copilot",
        ],
        risk_level=RiskLevel.HIGH,
        default_frameworks=["nist_ai_rmf", "soc2", "sig_2026"],
        data_types=["prompts", "training_data", "model_outputs"],
    ),
    VendorCategory.IDENTITY_ACCESS: CategoryDefinition(
        category=VendorCategory.IDENTITY_ACCESS,
        display_name="Identity & Access Management",
        description="Authentication, authorization, and identity management services",
        keywords=[
            "sso",
            "single sign-on",
            "identity",
            "iam",
            "authentication",
            "authorization",
            "okta",
            "auth0",
            "onelogin",
            "ping identity",
            "azure ad",
            "entra",
            "saml",
            "oauth",
            "oidc",
            "mfa",
            "2fa",
            "passwordless",
            "cyberark",
            "beyond trust",
            "pam",
            "privileged access",
        ],
        risk_level=RiskLevel.CRITICAL,
        default_frameworks=["sig_2026", "soc2", "nist_csf"],
        data_types=["credentials", "user_identities", "access_tokens"],
    ),
    VendorCategory.COMMUNICATION: CategoryDefinition(
        category=VendorCategory.COMMUNICATION,
        display_name="Communication & Messaging",
        description="Email, SMS, voice, and messaging services",
        keywords=[
            "sms",
            "email",
            "voice",
            "twilio",
            "sendgrid",
            "mailgun",
            "mailchimp",
            "messaging",
            "notification",
            "push notification",
            "vonage",
            "plivo",
            "bandwidth",
            "slack",
            "teams",
            "zoom",
            "webex",
            "discord",
            "intercom",
        ],
        risk_level=RiskLevel.HIGH,
        default_frameworks=["soc2", "sig_2026"],
        data_types=["contact_info", "message_content", "communication_logs"],
    ),
    VendorCategory.SECURITY_TOOLS: CategoryDefinition(
        category=VendorCategory.SECURITY_TOOLS,
        display_name="Security Tools",
        description="Security monitoring, endpoint protection, and vulnerability management",
        keywords=[
            "edr",
            "xdr",
            "siem",
            "security",
            "firewall",
            "antivirus",
            "endpoint protection",
            "crowdstrike",
            "sentinelone",
            "palo alto",
            "zscaler",
            "splunk",
            "elastic",
            "qualys",
            "tenable",
            "rapid7",
            "snyk",
            "veracode",
            "checkmarx",
            "sonarqube",
            "wiz",
            "orca",
            "vulnerability",
            "scanning",
            "penetration test",
        ],
        risk_level=RiskLevel.HIGH,
        default_frameworks=["sig_2026", "soc2", "nist_csf"],
        data_types=["security_logs", "vulnerability_data", "endpoint_telemetry"],
    ),
    VendorCategory.HR_CORPORATE: CategoryDefinition(
        category=VendorCategory.HR_CORPORATE,
        display_name="HR & Corporate Services",
        description="Human resources, payroll, benefits, and corporate services",
        keywords=[
            "hr",
            "human resources",
            "recruiting",
            "payroll",
            "benefits",
            "workday",
            "adp",
            "gusto",
            "rippling",
            "greenhouse",
            "lever",
            "bamboohr",
            "namely",
            "zenefits",
            "employee",
            "onboarding",
            "performance",
            "learning management",
            "lms",
            "docusign",
            "adobe sign",
        ],
        risk_level=RiskLevel.MEDIUM,
        default_frameworks=["soc2", "sig_2026"],
        data_types=["employee_pii", "payroll_data", "hr_records"],
    ),
    VendorCategory.MARKETING: CategoryDefinition(
        category=VendorCategory.MARKETING,
        display_name="Marketing & Advertising",
        description="Marketing automation, advertising platforms, and analytics",
        keywords=[
            "marketing",
            "advertising",
            "ads",
            "campaign",
            "hubspot",
            "marketo",
            "salesforce marketing",
            "pardot",
            "google ads",
            "facebook ads",
            "meta ads",
            "linkedin ads",
            "trade desk",
            "programmatic",
            "retargeting",
            "attribution",
            "branch",
            "appsflyer",
            "adjust",
            "crm",
            "customer relationship",
        ],
        risk_level=RiskLevel.MEDIUM,
        default_frameworks=["soc2", "sig_2026"],
        data_types=["customer_segments", "conversion_data", "ad_data"],
    ),
    VendorCategory.LOGISTICS: CategoryDefinition(
        category=VendorCategory.LOGISTICS,
        display_name="Logistics & Operations",
        description="Shipping, delivery, fleet management, and operations",
        keywords=[
            "logistics",
            "shipping",
            "delivery",
            "routing",
            "maps",
            "gps",
            "tracking",
            "fleet",
            "warehouse",
            "fulfillment",
            "google maps",
            "mapbox",
            "here",
            "fedex",
            "ups",
            "usps",
            "dhl",
            "shippo",
            "easypost",
            "project44",
            "driver",
            "courier",
        ],
        risk_level=RiskLevel.HIGH,
        default_frameworks=["soc2", "sig_2026"],
        data_types=["location_data", "delivery_info", "driver_data"],
    ),
    VendorCategory.HEALTHCARE: CategoryDefinition(
        category=VendorCategory.HEALTHCARE,
        display_name="Healthcare",
        description="Healthcare, telehealth, and medical services",
        keywords=[
            "healthcare",
            "health",
            "medical",
            "hipaa",
            "phi",
            "ehr",
            "electronic health record",
            "epic",
            "cerner",
            "telehealth",
            "telemedicine",
            "pharmacy",
            "prescription",
            "clinical",
            "patient",
            "doctor",
            "hospital",
            "insurance",
            "claims",
        ],
        risk_level=RiskLevel.CRITICAL,
        default_frameworks=["soc2", "sig_2026", "hipaa"],
        data_types=["phi", "medical_records", "health_data"],
    ),
    VendorCategory.EDUCATION: CategoryDefinition(
        category=VendorCategory.EDUCATION,
        display_name="Education",
        description="Educational technology and learning management systems",
        keywords=[
            "education",
            "edtech",
            "lms",
            "learning management",
            "canvas",
            "blackboard",
            "moodle",
            "coursera",
            "udemy",
            "student",
            "school",
            "university",
            "college",
            "ferpa",
            "classroom",
            "grading",
            "assessment",
            "curriculum",
            "e-learning",
        ],
        risk_level=RiskLevel.HIGH,
        default_frameworks=["hecvat", "soc2", "sig_2026"],
        data_types=["student_data", "ferpa_protected", "educational_records"],
    ),
    VendorCategory.DEVELOPMENT_TOOLS: CategoryDefinition(
        category=VendorCategory.DEVELOPMENT_TOOLS,
        display_name="Development Tools",
        description="Software development, DevOps, and collaboration tools",
        keywords=[
            "github",
            "gitlab",
            "bitbucket",
            "jira",
            "confluence",
            "devops",
            "ci/cd",
            "jenkins",
            "circleci",
            "travis",
            "terraform",
            "ansible",
            "puppet",
            "chef",
            "pagerduty",
            "opsgenie",
            "datadog",
            "new relic",
            "dynatrace",
            "apm",
            "monitoring",
            "observability",
        ],
        risk_level=RiskLevel.HIGH,
        default_frameworks=["soc2", "sig_2026", "caiq"],
        data_types=["source_code", "secrets", "build_artifacts"],
    ),
    VendorCategory.CUSTOMER_SUPPORT: CategoryDefinition(
        category=VendorCategory.CUSTOMER_SUPPORT,
        display_name="Customer Support",
        description="Customer support, helpdesk, and CRM systems",
        keywords=[
            "support",
            "helpdesk",
            "zendesk",
            "freshdesk",
            "servicenow",
            "salesforce service",
            "intercom",
            "drift",
            "chatbot",
            "live chat",
            "ticket",
            "ticketing",
            "customer service",
            "call center",
            "contact center",
            "ivr",
        ],
        risk_level=RiskLevel.MEDIUM,
        default_frameworks=["soc2", "sig_2026"],
        data_types=["support_tickets", "customer_info", "chat_logs"],
    ),
    VendorCategory.OTHER: CategoryDefinition(
        category=VendorCategory.OTHER,
        display_name="Other",
        description="Vendors that don't fit into standard categories",
        keywords=[],
        risk_level=RiskLevel.MEDIUM,
        default_frameworks=["soc2", "sig_2026"],
        data_types=["varies"],
    ),
}


@dataclass
class CategorizationResult:
    """Result of vendor categorization analysis."""

    primary_category: VendorCategory
    confidence: float
    risk_level: RiskLevel
    recommended_frameworks: list[str]
    matched_keywords: list[str]
    secondary_categories: list[VendorCategory]
    data_types: list[str]
    assessment_priority: str  # "immediate", "standard", "deferred"


def categorize_vendor(
    vendor_name: str,
    vendor_description: str | None = None,
    service_type: str | None = None,
    additional_context: str | None = None,
) -> CategorizationResult:
    """Automatically categorize a vendor based on available information.

    Args:
        vendor_name: Name of the vendor
        vendor_description: Optional description of the vendor/service
        service_type: Optional type of service provided
        additional_context: Any additional context about the vendor

    Returns:
        CategorizationResult with category, risk level, and recommended frameworks
    """
    # Combine all available text for analysis
    search_text = " ".join(
        filter(None, [vendor_name, vendor_description, service_type, additional_context])
    ).lower()

    # Score each category based on keyword matches
    category_scores: dict[VendorCategory, tuple[float, list[str]]] = {}

    for category, definition in CATEGORY_DEFINITIONS.items():
        if category == VendorCategory.OTHER:
            continue

        matches: list[str] = []
        for keyword in definition.keywords:
            if keyword.lower() in search_text:
                matches.append(keyword)

        if matches:
            # Score based on number of unique matches and keyword specificity
            score = len(matches) + (len(set(matches)) * 0.5)
            category_scores[category] = (score, matches)

    if not category_scores:
        # No matches found, default to OTHER
        return CategorizationResult(
            primary_category=VendorCategory.OTHER,
            confidence=0.3,
            risk_level=RiskLevel.MEDIUM,
            recommended_frameworks=["soc2", "sig_2026"],
            matched_keywords=[],
            secondary_categories=[],
            data_types=["unknown"],
            assessment_priority="standard",
        )

    # Sort categories by score
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1][0], reverse=True)

    primary_category = sorted_categories[0][0]
    primary_score, matched_keywords = sorted_categories[0][1]
    primary_definition = CATEGORY_DEFINITIONS[primary_category]

    # Calculate confidence based on score and uniqueness
    max_possible_score = len(primary_definition.keywords) * 1.5
    confidence = min(primary_score / max(max_possible_score, 1), 1.0)
    confidence = max(confidence, 0.4)  # Minimum confidence if we have matches

    # Get secondary categories (others with significant scores)
    secondary_categories = [
        cat for cat, (score, _) in sorted_categories[1:4] if score >= primary_score * 0.5
    ]

    # Determine assessment priority based on risk level
    if primary_definition.risk_level == RiskLevel.CRITICAL:
        assessment_priority = "immediate"
    elif primary_definition.risk_level == RiskLevel.HIGH:
        assessment_priority = "standard"
    else:
        assessment_priority = "deferred"

    return CategorizationResult(
        primary_category=primary_category,
        confidence=round(confidence, 2),
        risk_level=primary_definition.risk_level,
        recommended_frameworks=primary_definition.default_frameworks,
        matched_keywords=list(set(matched_keywords)),
        secondary_categories=secondary_categories,
        data_types=primary_definition.data_types,
        assessment_priority=assessment_priority,
    )


def get_framework_recommendations(
    category: VendorCategory,
    data_types: list[str] | None = None,
    is_eu_vendor: bool = False,
    is_financial_entity: bool = False,
    handles_student_data: bool = False,
    handles_health_data: bool = False,
) -> list[str]:
    """Get framework recommendations based on vendor characteristics.

    Args:
        category: Primary vendor category
        data_types: Types of data the vendor processes
        is_eu_vendor: Whether the vendor operates in the EU
        is_financial_entity: Whether the vendor is a financial entity
        handles_student_data: Whether the vendor handles student data
        handles_health_data: Whether the vendor handles health data

    Returns:
        List of recommended framework IDs
    """
    frameworks: list[str] = []

    # Get base recommendations from category
    if category in CATEGORY_DEFINITIONS:
        frameworks.extend(CATEGORY_DEFINITIONS[category].default_frameworks)

    # Add regulatory frameworks based on characteristics
    if is_eu_vendor or is_financial_entity:
        if "dora" not in frameworks:
            frameworks.append("dora")

    if handles_student_data:
        if "hecvat" not in frameworks:
            frameworks.insert(0, "hecvat")

    if handles_health_data:
        # HIPAA framework would be added here when available
        pass

    # Ensure AI RMF is included for AI vendors
    if category == VendorCategory.AI_ML and "nist_ai_rmf" not in frameworks:
        frameworks.insert(0, "nist_ai_rmf")

    return list(dict.fromkeys(frameworks))  # Remove duplicates while preserving order


def get_category_info(category: VendorCategory) -> dict[str, Any]:
    """Get detailed information about a vendor category.

    Args:
        category: The vendor category

    Returns:
        Dictionary with category details
    """
    if category not in CATEGORY_DEFINITIONS:
        return {}

    definition = CATEGORY_DEFINITIONS[category]
    return {
        "id": definition.category.value,
        "display_name": definition.display_name,
        "description": definition.description,
        "risk_level": definition.risk_level.value,
        "default_frameworks": definition.default_frameworks,
        "typical_data_types": definition.data_types,
        "keyword_examples": definition.keywords[:10],  # First 10 keywords as examples
    }


def get_all_categories() -> list[dict[str, Any]]:
    """Get information about all available vendor categories.

    Returns:
        List of category information dictionaries
    """
    return [
        get_category_info(category)
        for category in VendorCategory
        if category != VendorCategory.OTHER
    ]


# Example vendor database for reference (based on DoorDash-like ecosystem)
EXAMPLE_VENDOR_TAXONOMY: dict[str, dict[str, Any]] = {
    "aws": {
        "name": "Amazon Web Services",
        "category": VendorCategory.CLOUD_INFRASTRUCTURE,
        "risk_level": RiskLevel.CRITICAL,
        "service_description": "Primary cloud infrastructure provider",
        "data_access": ["full_production_data", "infrastructure_config"],
        "frameworks": ["soc2", "caiq", "iso27001", "fedramp"],
    },
    "snowflake": {
        "name": "Snowflake",
        "category": VendorCategory.DATA_ANALYTICS,
        "risk_level": RiskLevel.CRITICAL,
        "service_description": "Data warehouse platform",
        "data_access": ["customer_pii", "analytics_data"],
        "frameworks": ["soc2", "sig_2026"],
        "breach_history": "Affected by 2024 credential stuffing attacks",
    },
    "stripe": {
        "name": "Stripe",
        "category": VendorCategory.PAYMENT_FINANCIAL,
        "risk_level": RiskLevel.CRITICAL,
        "service_description": "Payment processing",
        "data_access": ["payment_data", "pci_scope"],
        "frameworks": ["pci_dss", "soc2", "soc1"],
    },
    "okta": {
        "name": "Okta",
        "category": VendorCategory.IDENTITY_ACCESS,
        "risk_level": RiskLevel.CRITICAL,
        "service_description": "Identity and access management",
        "data_access": ["user_credentials", "access_tokens"],
        "frameworks": ["soc2", "iso27001", "fedramp"],
    },
    "openai": {
        "name": "OpenAI",
        "category": VendorCategory.AI_ML,
        "risk_level": RiskLevel.HIGH,
        "service_description": "AI/LLM services",
        "data_access": ["prompts", "conversation_data"],
        "frameworks": ["soc2", "nist_ai_rmf"],
    },
    "twilio": {
        "name": "Twilio",
        "category": VendorCategory.COMMUNICATION,
        "risk_level": RiskLevel.HIGH,
        "service_description": "SMS and voice communications",
        "data_access": ["phone_numbers", "message_content"],
        "frameworks": ["soc2", "iso27001"],
    },
    "datadog": {
        "name": "Datadog",
        "category": VendorCategory.DEVELOPMENT_TOOLS,
        "risk_level": RiskLevel.HIGH,
        "service_description": "Monitoring and observability",
        "data_access": ["system_metrics", "logs", "traces"],
        "frameworks": ["soc2", "iso27001"],
    },
    "workday": {
        "name": "Workday",
        "category": VendorCategory.HR_CORPORATE,
        "risk_level": RiskLevel.MEDIUM,
        "service_description": "HR and payroll system",
        "data_access": ["employee_pii", "payroll_data"],
        "frameworks": ["soc2", "soc1"],
    },
    "zendesk": {
        "name": "Zendesk",
        "category": VendorCategory.CUSTOMER_SUPPORT,
        "risk_level": RiskLevel.MEDIUM,
        "service_description": "Customer support platform",
        "data_access": ["support_tickets", "customer_info"],
        "frameworks": ["soc2"],
    },
    "google_maps": {
        "name": "Google Maps Platform",
        "category": VendorCategory.LOGISTICS,
        "risk_level": RiskLevel.HIGH,
        "service_description": "Mapping and routing services",
        "data_access": ["location_data", "route_info"],
        "frameworks": ["soc2", "iso27001"],
    },
}
