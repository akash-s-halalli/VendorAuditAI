"""Prompt templates for RAG-based compliance analysis.

This module provides structured prompt templates for:
- Compliance analysis against various frameworks
- Finding generation with detailed citations
- Severity assessment and remediation guidance
"""

from app.prompts.compliance_analysis import (
    COMPLIANCE_ANALYSIS_SYSTEM_PROMPT,
    build_compliance_analysis_prompt,
    get_framework_context,
)
from app.prompts.finding_generation import (
    FINDING_GENERATION_SYSTEM_PROMPT,
    build_finding_detail_prompt,
    build_multi_finding_prompt,
)

__all__ = [
    "COMPLIANCE_ANALYSIS_SYSTEM_PROMPT",
    "FINDING_GENERATION_SYSTEM_PROMPT",
    "build_compliance_analysis_prompt",
    "build_finding_detail_prompt",
    "build_multi_finding_prompt",
    "get_framework_context",
]
