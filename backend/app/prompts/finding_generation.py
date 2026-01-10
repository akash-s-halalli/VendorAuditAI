"""Prompt templates for generating detailed findings with citations.

This module provides structured prompts for:
- Generating detailed finding descriptions
- Creating actionable remediation guidance
- Assessing severity and business impact
- Building citations with page-specific references
"""

from typing import Any

# System prompt for finding generation
FINDING_GENERATION_SYSTEM_PROMPT = """You are an expert compliance analyst generating detailed security findings for vendor risk assessments. Your findings must be:

1. **Evidence-Based**: Every claim must be supported by specific text from the document
2. **Actionable**: Provide clear, implementable remediation steps
3. **Business-Focused**: Explain the real-world impact of each finding
4. **Properly Cited**: Include exact page numbers and quoted text

## Severity Assessment Criteria

**CRITICAL** (Immediate action required)
- Complete absence of a fundamental security control
- Active security incident or vulnerability being exploited
- Regulatory violation with significant penalties
- Direct risk to customer data or business continuity
- Examples: No encryption for data in transit, no access controls, no backup/recovery

**HIGH** (Urgent remediation within 30 days)
- Significant control weakness or gap
- Material weakness in security posture
- High likelihood of exploitation
- Substantial regulatory or contractual risk
- Examples: Weak password policies, missing MFA, inadequate logging

**MEDIUM** (Remediation within 90 days)
- Partial control implementation
- Control exists but effectiveness is questionable
- Moderate risk if exploited
- Potential compliance gap
- Examples: Incomplete asset inventory, infrequent access reviews, partial encryption

**LOW** (Remediation within 180 days)
- Minor gap or documentation issue
- Control implemented but could be improved
- Low exploitation likelihood
- Best practice improvement opportunity
- Examples: Policy update needed, training frequency, minor documentation gaps

**INFO** (No immediate action required)
- Observation or recommendation
- Positive finding or strength noted
- Future improvement suggestion
- Context or clarification provided

## Citation Requirements

Every finding must include:
1. The exact excerpt number from the provided context
2. The page number where the evidence was found
3. A direct quote from the document (not paraphrased)
4. Explanation of why this quote supports the finding

Always respond in valid JSON format as specified."""


def build_finding_detail_prompt(
    chunk_content: str,
    framework_control: str,
    control_description: str,
    initial_concern: str,
    chunk_metadata: dict[str, Any] | None = None,
) -> str:
    """Build a prompt for generating detailed finding information.

    Args:
        chunk_content: The document content being analyzed
        framework_control: The specific control ID being assessed
        control_description: Description of the control requirement
        initial_concern: The initial concern or gap identified
        chunk_metadata: Optional metadata (page_number, section_header, chunk_id)

    Returns:
        Formatted prompt string for finding generation
    """
    metadata_section = ""
    if chunk_metadata:
        page = chunk_metadata.get("page_number", "Unknown")
        section = chunk_metadata.get("section_header", "Unknown")
        chunk_id = chunk_metadata.get("chunk_id", "Unknown")
        metadata_section = f"""
**Source Information**:
- Page Number: {page}
- Section: {section}
- Chunk ID: {chunk_id}
"""

    return f"""## Finding Detail Generation Request

Generate a detailed finding assessment based on the following information.

### Framework Control
**Control ID**: {framework_control}
**Control Requirement**: {control_description}

### Initial Concern Identified
{initial_concern}

### Document Excerpt
{metadata_section}
```
{chunk_content}
```

---

## Required Output

Provide a comprehensive finding assessment in JSON format:

```json
{{
    "title": "Clear, specific finding title (max 100 characters)",
    "severity": "critical|high|medium|low|info",
    "severity_justification": "Explanation of why this severity level was assigned",
    "framework_control": "{framework_control}",
    "description": "Detailed description of the finding (2-4 paragraphs)",
    "evidence": {{
        "page_number": <page number or null>,
        "section_header": "<section header or null>",
        "quoted_text": "Exact quote from the document that supports this finding",
        "context": "Explanation of how this quote demonstrates the gap"
    }},
    "business_impact": {{
        "description": "Description of potential business impact",
        "risk_scenarios": [
            "Specific scenario 1 that could result from this gap",
            "Specific scenario 2 that could result from this gap"
        ],
        "affected_areas": ["data_security", "availability", "compliance", "reputation"]
    }},
    "remediation": {{
        "summary": "One-sentence summary of required action",
        "detailed_steps": [
            "Step 1: Specific action to take",
            "Step 2: Follow-up action",
            "Step 3: Verification step"
        ],
        "timeline": "Recommended timeline for remediation",
        "resources_needed": "Resources or expertise required"
    }},
    "related_controls": [
        "List of related control IDs that may also be affected"
    ],
    "confidence_score": 0.0-1.0,
    "confidence_explanation": "Why this confidence level was assigned"
}}
```

**Important**:
- The quoted_text must be an exact quote from the document excerpt provided
- If the excerpt does not contain clear evidence, indicate this in the confidence_explanation
- Severity must align with the criteria provided in your system prompt
"""


def build_multi_finding_prompt(
    document_context: str,
    findings_to_detail: list[dict[str, Any]],
    framework_id: str,
    framework_controls: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Build a prompt for generating details for multiple findings.

    Args:
        document_context: Full document context with all relevant chunks
        findings_to_detail: List of initial findings that need detailed expansion
        framework_id: The compliance framework being assessed
        framework_controls: Optional dict of control_id -> control details

    Returns:
        Formatted prompt string for multi-finding generation
    """
    findings_section = []
    for i, finding in enumerate(findings_to_detail, 1):
        control_id = finding.get("framework_control", "Unknown")
        control_details = ""
        if framework_controls and control_id in framework_controls:
            ctrl = framework_controls[control_id]
            control_details = f"\n   Control Description: {ctrl.get('description', 'N/A')}"

        findings_section.append(
            f"""
### Finding {i}
- **Title**: {finding.get('title', 'Untitled')}
- **Control**: {control_id}{control_details}
- **Initial Severity**: {finding.get('severity', 'medium')}
- **Initial Description**: {finding.get('description', 'No description')}
- **Excerpt Reference**: {finding.get('excerpt_number', 'Unknown')}
"""
        )

    return f"""## Multi-Finding Detail Generation

Generate detailed assessments for the following findings identified during compliance analysis.

### Framework: {framework_id.upper()}

### Document Context

{document_context}

---

## Findings Requiring Detailed Assessment
{"".join(findings_section)}
---

## Required Output

Provide detailed assessments for ALL findings in JSON format:

```json
{{
    "detailed_findings": [
        {{
            "original_title": "Original finding title",
            "enhanced_title": "Improved, more specific title",
            "severity": "critical|high|medium|low|info",
            "severity_justification": "Why this severity level",
            "framework_control": "Control ID",
            "description": "Comprehensive description (2-4 paragraphs)",
            "evidence": {{
                "excerpt_number": 1,
                "page_number": 5,
                "quoted_text": "Exact quote from document",
                "relevance": "How this quote supports the finding"
            }},
            "business_impact": "Real-world impact of this gap",
            "remediation": {{
                "summary": "Brief remediation summary",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "priority": "immediate|short_term|medium_term|long_term"
            }},
            "confidence_score": 0.85
        }}
    ],
    "cross_cutting_themes": [
        {{
            "theme": "Common issue identified across multiple findings",
            "affected_findings": [1, 3, 5],
            "root_cause_analysis": "Potential root cause",
            "consolidated_recommendation": "Single action to address multiple findings"
        }}
    ],
    "prioritized_actions": [
        {{
            "rank": 1,
            "action": "Most important action to take",
            "findings_addressed": [1, 2],
            "rationale": "Why this is the top priority"
        }}
    ]
}}
```

**Instructions**:
1. Enhance each finding with more specific details and evidence
2. Ensure all evidence references exact quotes from the document context
3. Identify any cross-cutting themes or root causes
4. Provide prioritized remediation actions
5. Adjust severity levels if detailed analysis warrants changes
"""


def build_citation_extraction_prompt(
    document_chunks: list[dict[str, Any]],
    finding_description: str,
    framework_control: str,
) -> str:
    """Build a prompt for extracting precise citations for a finding.

    Args:
        document_chunks: List of document chunks to search for evidence
        finding_description: Description of the finding needing citations
        framework_control: The control being assessed

    Returns:
        Formatted prompt string for citation extraction
    """
    chunks_text = []
    for i, chunk in enumerate(document_chunks, 1):
        page = chunk.get("page_number", "?")
        section = chunk.get("section_header", "Unknown Section")
        content = chunk.get("content", "")
        chunks_text.append(
            f"""
--- Chunk {i} [Page: {page}] [Section: {section}] ---
{content}
"""
        )

    return f"""## Citation Extraction Request

Find the most relevant citations to support the following finding.

### Finding Details
**Control**: {framework_control}
**Description**: {finding_description}

### Document Chunks to Search
{"".join(chunks_text)}
---

## Required Output

Identify all relevant citations in JSON format:

```json
{{
    "primary_citation": {{
        "chunk_number": 1,
        "page_number": 5,
        "section_header": "Section name",
        "quoted_text": "Exact quote that best supports the finding",
        "relevance_score": 0.95,
        "explanation": "Why this is the primary evidence"
    }},
    "supporting_citations": [
        {{
            "chunk_number": 3,
            "page_number": 12,
            "section_header": "Section name",
            "quoted_text": "Additional supporting quote",
            "relevance_score": 0.75,
            "explanation": "How this adds to the evidence"
        }}
    ],
    "contradicting_evidence": [
        {{
            "chunk_number": 5,
            "page_number": 20,
            "quoted_text": "Quote that might contradict the finding",
            "explanation": "How this affects the finding assessment"
        }}
    ],
    "evidence_strength": "strong|moderate|weak|insufficient",
    "confidence_notes": "Any notes about the quality or completeness of evidence"
}}
```

**Instructions**:
1. Find the single best quote that most directly supports the finding
2. Include any additional supporting evidence
3. Note any contradicting evidence that might affect the assessment
4. All quoted_text must be exact copies from the document chunks
5. Relevance scores should reflect how directly the quote supports the finding
"""


def build_remediation_prompt(
    finding_title: str,
    finding_description: str,
    framework_control: str,
    control_requirements: list[dict[str, Any]] | None = None,
    organization_context: str | None = None,
) -> str:
    """Build a prompt for generating detailed remediation guidance.

    Args:
        finding_title: Title of the finding
        finding_description: Detailed description of the finding
        framework_control: The framework control being addressed
        control_requirements: Optional list of specific requirements for the control
        organization_context: Optional context about the organization's environment

    Returns:
        Formatted prompt string for remediation generation
    """
    requirements_section = ""
    if control_requirements:
        req_text = []
        for req in control_requirements:
            req_text.append(
                f"- **{req.get('id', 'N/A')}**: {req.get('description', 'No description')}"
            )
            if req.get("guidance"):
                req_text.append(f"  - Guidance: {req.get('guidance')}")
        requirements_section = f"""
### Control Requirements to Address
{chr(10).join(req_text)}
"""

    context_section = ""
    if organization_context:
        context_section = f"""
### Organization Context
{organization_context}
"""

    return f"""## Remediation Guidance Generation

Generate comprehensive remediation guidance for the following finding.

### Finding Information
**Title**: {finding_title}
**Framework Control**: {framework_control}
**Description**: {finding_description}
{requirements_section}{context_section}
---

## Required Output

Provide detailed remediation guidance in JSON format:

```json
{{
    "remediation_plan": {{
        "objective": "Clear statement of what the remediation will achieve",
        "approach": "High-level approach to addressing the finding"
    }},
    "immediate_actions": [
        {{
            "action": "Immediate action to take",
            "responsible_party": "Role responsible",
            "timeline": "Within X days",
            "success_criteria": "How to verify completion"
        }}
    ],
    "short_term_actions": [
        {{
            "action": "Action to take within 30 days",
            "responsible_party": "Role responsible",
            "dependencies": ["List of dependencies"],
            "success_criteria": "How to verify completion"
        }}
    ],
    "long_term_actions": [
        {{
            "action": "Action for sustained improvement",
            "responsible_party": "Role responsible",
            "timeline": "Ongoing or specific date",
            "success_criteria": "How to verify completion"
        }}
    ],
    "resource_requirements": {{
        "personnel": ["Roles or skills needed"],
        "tools": ["Software or tools that may help"],
        "budget_considerations": "Estimated cost or budget impact",
        "external_support": "Any external consultants or services needed"
    }},
    "verification_steps": [
        "Step 1: How to verify the fix is working",
        "Step 2: Ongoing monitoring approach"
    ],
    "documentation_updates": [
        "Policies or procedures that need to be updated"
    ],
    "potential_challenges": [
        {{
            "challenge": "Potential obstacle",
            "mitigation": "How to address it"
        }}
    ],
    "compliance_evidence": [
        "Evidence to collect to demonstrate compliance"
    ]
}}
```

**Instructions**:
1. Provide actionable, specific steps (not generic advice)
2. Consider resource constraints typical of organizations
3. Include verification steps to confirm remediation success
4. Identify potential challenges and how to overcome them
5. Specify what evidence to collect for compliance demonstration
"""
