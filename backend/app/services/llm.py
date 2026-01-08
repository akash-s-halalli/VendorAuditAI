"""LLM service for Claude-based document analysis."""

import json
from dataclasses import dataclass, field
from typing import Any, List

from anthropic import AsyncAnthropic

from app.config import get_settings


@dataclass
class AnalysisResult:
    """Result from LLM analysis."""

    findings: List[dict] = field(default_factory=list)
    summary: str = ""
    raw_response: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class Citation:
    """Citation reference for a finding."""

    chunk_id: str
    content_excerpt: str
    page_number: int | None = None
    section_header: str | None = None
    relevance_score: float = 0.0


class ClaudeService:
    """Service for interacting with Claude API for document analysis.

    Uses Claude to analyze compliance documents against frameworks
    and generate findings with citations.
    """

    # System prompt for compliance analysis
    ANALYSIS_SYSTEM_PROMPT = """You are an expert compliance analyst specializing in vendor security assessments. You analyze security documents (SOC 2 reports, SIG questionnaires, HECVAT forms, ISO 27001 certifications) against compliance frameworks.

Your task is to:
1. Analyze the provided document excerpts
2. Identify gaps, concerns, or findings based on the specified framework
3. Provide evidence-based findings with specific citations

For each finding, you must provide:
- A clear, actionable title
- Severity level: critical, high, medium, low, or info
- Detailed description of the issue
- The specific framework control or requirement being assessed
- Evidence from the document (quote the relevant text)
- Remediation recommendation

Respond in JSON format only."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        """Initialize the Claude service.

        Args:
            api_key: Anthropic API key (uses settings if not provided)
            model: Model name (uses settings if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.claude_model

        if not self.api_key:
            self._client = None
        else:
            self._client = AsyncAnthropic(api_key=self.api_key)

    @property
    def is_configured(self) -> bool:
        """Check if the service has valid API credentials."""
        return self._client is not None

    async def analyze_document(
        self,
        chunks: List[dict],
        framework: str,
        document_type: str,
        max_tokens: int = 4096,
    ) -> AnalysisResult:
        """Analyze document chunks against a compliance framework.

        Args:
            chunks: List of chunk dicts with 'content', 'section_header', 'page_number'
            framework: Framework to analyze against (e.g., 'nist_800_53', 'soc2_tsc')
            document_type: Type of document (e.g., 'soc2', 'sig_lite')
            max_tokens: Maximum tokens in response

        Returns:
            AnalysisResult with findings and metadata

        Raises:
            ValueError: If service not configured or API error
        """
        if not self.is_configured:
            raise ValueError("Anthropic API key not configured")

        # Build context from chunks
        context = self._build_context(chunks)

        # Build the analysis prompt
        prompt = self._build_analysis_prompt(context, framework, document_type)

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.ANALYSIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse the response
            raw_text = response.content[0].text
            findings = self._parse_findings(raw_text)

            return AnalysisResult(
                findings=findings,
                summary=self._extract_summary(findings),
                raw_response=raw_text,
                model=self.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )

        except Exception as e:
            raise ValueError(f"Analysis failed: {str(e)}")

    async def generate_finding_details(
        self,
        chunk_content: str,
        framework_control: str,
        initial_concern: str,
        max_tokens: int = 2048,
    ) -> dict:
        """Generate detailed finding information for a specific concern.

        Args:
            chunk_content: The document content being analyzed
            framework_control: The specific control being assessed
            initial_concern: The initial concern identified
            max_tokens: Maximum tokens in response

        Returns:
            Dict with detailed finding information
        """
        if not self.is_configured:
            raise ValueError("Anthropic API key not configured")

        prompt = f"""Analyze this document excerpt and provide a detailed finding assessment.

Document Excerpt:
{chunk_content}

Framework Control: {framework_control}
Initial Concern: {initial_concern}

Provide a detailed assessment in JSON format:
{{
    "title": "Brief finding title",
    "severity": "critical|high|medium|low|info",
    "description": "Detailed description of the finding",
    "evidence": "Specific quote from the document",
    "impact": "Business impact of this finding",
    "remediation": "Recommended remediation steps",
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            raw_text = response.content[0].text
            return self._parse_json_response(raw_text)

        except Exception as e:
            raise ValueError(f"Finding generation failed: {str(e)}")

    async def answer_query(
        self,
        query: str,
        context_chunks: List[dict],
        max_tokens: int = 2048,
    ) -> dict:
        """Answer a natural language query about the documents.

        Args:
            query: User's question
            context_chunks: Relevant chunks for context
            max_tokens: Maximum tokens in response

        Returns:
            Dict with answer and citations
        """
        if not self.is_configured:
            raise ValueError("Anthropic API key not configured")

        context = self._build_context(context_chunks)

        prompt = f"""Based on the following document excerpts, answer the user's question.

Document Context:
{context}

User Question: {query}

Provide your answer in JSON format:
{{
    "answer": "Your detailed answer",
    "confidence": 0.0-1.0,
    "citations": [
        {{
            "chunk_index": 0,
            "excerpt": "relevant quote",
            "relevance": "why this is relevant"
        }}
    ],
    "limitations": "Any limitations or caveats"
}}"""

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            raw_text = response.content[0].text
            return self._parse_json_response(raw_text)

        except Exception as e:
            raise ValueError(f"Query failed: {str(e)}")

    def _build_context(self, chunks: List[dict]) -> str:
        """Build context string from chunks."""
        context_parts = []
        for i, chunk in enumerate(chunks):
            header = chunk.get("section_header", "")
            page = chunk.get("page_number")
            content = chunk.get("content", "")

            header_line = f"[Section: {header}]" if header else ""
            page_line = f"[Page: {page}]" if page else ""

            context_parts.append(
                f"--- Excerpt {i + 1} {header_line} {page_line} ---\n{content}"
            )

        return "\n\n".join(context_parts)

    def _build_analysis_prompt(
        self,
        context: str,
        framework: str,
        document_type: str,
    ) -> str:
        """Build the analysis prompt."""
        framework_desc = FRAMEWORK_DESCRIPTIONS.get(
            framework, f"compliance framework: {framework}"
        )

        return f"""Analyze the following {document_type.upper()} document excerpts against {framework_desc}.

Document Content:
{context}

Identify any gaps, concerns, or findings. Focus on:
1. Missing or incomplete controls
2. Vague or insufficient evidence
3. Scope limitations or exclusions
4. Areas requiring follow-up

Respond with a JSON object:
{{
    "findings": [
        {{
            "title": "Finding title",
            "severity": "critical|high|medium|low|info",
            "framework_control": "Specific control reference",
            "description": "Detailed description",
            "evidence": "Quote from document",
            "remediation": "Recommended action"
        }}
    ],
    "overall_assessment": "Brief overall assessment",
    "confidence_score": 0.0-1.0
}}"""

    def _parse_findings(self, response_text: str) -> List[dict]:
        """Parse findings from Claude response."""
        try:
            data = self._parse_json_response(response_text)
            return data.get("findings", [])
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, return empty list
            return []

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from response text."""
        # Try to find JSON in the response
        text = text.strip()

        # If wrapped in markdown code blocks, extract
        if text.startswith("```"):
            lines = text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```json"):
                    in_json = True
                    continue
                elif line.startswith("```"):
                    in_json = False
                    continue
                if in_json:
                    json_lines.append(line)
            text = "\n".join(json_lines)

        return json.loads(text)

    def _extract_summary(self, findings: List[dict]) -> str:
        """Generate a summary from findings."""
        if not findings:
            return "No significant findings identified."

        severity_counts = {}
        for finding in findings:
            severity = finding.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        summary_parts = []
        for severity in ["critical", "high", "medium", "low", "info"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                summary_parts.append(f"{count} {severity}")

        return f"Analysis identified: {', '.join(summary_parts)} findings."


# Framework descriptions for prompts
FRAMEWORK_DESCRIPTIONS = {
    "nist_800_53": "NIST 800-53 Security and Privacy Controls",
    "soc2_tsc": "SOC 2 Trust Service Criteria",
    "iso_27001": "ISO 27001 Information Security Management",
    "cis_controls": "CIS Critical Security Controls v8",
    "hipaa": "HIPAA Security Rule",
    "pci_dss": "PCI DSS v4.0 Requirements",
}

# Supported frameworks
SUPPORTED_FRAMEWORKS = list(FRAMEWORK_DESCRIPTIONS.keys())


# Default service instance
_claude_service: ClaudeService | None = None


def get_claude_service() -> ClaudeService:
    """Get or create the default Claude service."""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
