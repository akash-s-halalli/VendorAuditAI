"""LLM service for document analysis with multiple provider support.

This module provides LLM integration for:
- Document compliance analysis using RAG
- Finding generation with citations
- Natural language queries about documents

Supported providers:
- Google Gemini (default)
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.config import get_settings


# Framework descriptions for prompts
FRAMEWORK_DESCRIPTIONS = {
    "nist_800_53": "NIST 800-53 Security and Privacy Controls",
    "soc2_tsc": "SOC 2 Trust Service Criteria",
    "iso_27001": "ISO 27001 Information Security Management",
    "cis_controls": "CIS Critical Security Controls v8",
    "hipaa": "HIPAA Security Rule",
    "pci_dss": "PCI DSS v4.0 Requirements",
    "caiq": "CSA Cloud Controls Matrix (CAIQ) v4.0",
    "nist_ai_rmf": "NIST AI Risk Management Framework 1.0",
    "ai_risk": "AI Vendor Risk Assessment Framework (Data Provenance, Model Security, Bias)",
}

# Supported frameworks
SUPPORTED_FRAMEWORKS = list(FRAMEWORK_DESCRIPTIONS.keys())


@dataclass
class AnalysisResult:
    """Result from LLM analysis."""

    findings: list[dict] = field(default_factory=list)
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


class BaseLLMService(ABC):
    """Abstract base class for LLM services.

    Defines the interface that all LLM providers must implement.
    Includes shared utility methods for parsing and formatting.
    """

    # System prompt for compliance analysis (shared across providers)
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

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the service has valid API credentials."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the model name being used."""
        pass

    @abstractmethod
    async def analyze_document(
        self,
        chunks: list[dict],
        framework: str,
        document_type: str,
        max_tokens: int = 4096,
    ) -> AnalysisResult:
        """Analyze document chunks against a compliance framework."""
        pass

    @abstractmethod
    async def analyze_document_with_prompt(
        self,
        prompt: str,
        framework: str,
        document_type: str | None = None,
        max_tokens: int = 8192,
    ) -> AnalysisResult:
        """Analyze document using a pre-built prompt."""
        pass

    @abstractmethod
    async def generate_finding_details(
        self,
        chunk_content: str,
        framework_control: str,
        initial_concern: str,
        max_tokens: int = 2048,
    ) -> dict:
        """Generate detailed finding information for a specific concern."""
        pass

    @abstractmethod
    async def answer_query(
        self,
        query: str,
        context_chunks: list[dict],
        max_tokens: int = 2048,
    ) -> dict:
        """Answer a natural language query about the documents."""
        pass

    # Shared utility methods (non-abstract)

    def _build_context(self, chunks: list[dict]) -> str:
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

    def _parse_findings(self, response_text: str) -> list[dict]:
        """Parse findings from LLM response."""
        try:
            data = self._parse_json_response(response_text)
            return data.get("findings", [])
        except (json.JSONDecodeError, ValueError):
            return []

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from response text."""
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

    def _parse_enhanced_response(self, text: str) -> dict:
        """Parse enhanced response format from compliance analysis."""
        try:
            parsed = self._parse_json_response(text)

            findings = parsed.get("findings", [])
            for finding in findings:
                conf = finding.get("confidence")
                if conf is not None:
                    try:
                        finding["confidence"] = float(conf)
                    except (ValueError, TypeError):
                        finding["confidence"] = 0.5

                if "severity" in finding:
                    finding["severity"] = str(finding["severity"]).lower()

            return parsed

        except (json.JSONDecodeError, ValueError):
            return {"findings": [], "overall_assessment": {}}

    def _extract_summary(self, findings: list[dict]) -> str:
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





class GeminiService(BaseLLMService):
    """Service for interacting with Google Gemini API for document analysis."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize the Gemini service.

        Args:
            api_key: Google API key (uses settings if not provided)
            model: Model name (uses settings if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self._model = model or settings.gemini_model
        self._genai_model = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._genai_model = genai.GenerativeModel(self._model)
            except ImportError:
                pass

    @property
    def is_configured(self) -> bool:
        """Check if the service has valid API credentials."""
        return self._genai_model is not None

    @property
    def model(self) -> str:
        """Return the model name being used."""
        return self._model

    async def _generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
    ) -> tuple[str, int, int]:
        """Generate content using Gemini API.

        Args:
            prompt: The prompt to send
            system: Optional system prompt (prepended to prompt)
            max_tokens: Maximum tokens in response

        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        import asyncio
        import google.generativeai as genai

        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        # If system instruction provided, create a new model with it
        if system:
            model_with_system = genai.GenerativeModel(
                model_name=self._model,
                system_instruction=system
            )
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model_with_system.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.1,
                    ),
                ),
            )
        else:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._genai_model.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.1,
                    ),
                ),
            )

        input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
        output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
        return response.text, input_tokens, output_tokens

    async def analyze_document(
        self,
        chunks: list[dict],
        framework: str,
        document_type: str,
        max_tokens: int = 4096,
    ) -> AnalysisResult:
        """Analyze document chunks against a compliance framework."""
        if not self.is_configured:
            raise ValueError("Google API key not configured")

        context = self._build_context(chunks)
        prompt = self._build_analysis_prompt(context, framework, document_type)
        raw_text, input_tokens, output_tokens = await self._generate(
            prompt, self.ANALYSIS_SYSTEM_PROMPT, max_tokens
        )
        findings = self._parse_findings(raw_text)

        return AnalysisResult(
            findings=findings,
            summary=self._extract_summary(findings),
            raw_response=raw_text,
            model=self._model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    async def analyze_document_with_prompt(
        self,
        prompt: str,
        framework: str,
        document_type: str | None = None,
        max_tokens: int = 8192,
    ) -> AnalysisResult:
        """Analyze document using a pre-built prompt."""
        if not self.is_configured:
            raise ValueError("Google API key not configured")

        from app.prompts.compliance_analysis import COMPLIANCE_ANALYSIS_SYSTEM_PROMPT

        raw_text, input_tokens, output_tokens = await self._generate(
            prompt, COMPLIANCE_ANALYSIS_SYSTEM_PROMPT, max_tokens
        )
        parsed = self._parse_enhanced_response(raw_text)
        findings = parsed.get("findings", [])
        summary = parsed.get("overall_assessment", {}).get(
            "summary", self._extract_summary(findings)
        )

        return AnalysisResult(
            findings=findings,
            summary=summary,
            raw_response=raw_text,
            model=self._model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    async def generate_finding_details(
        self,
        chunk_content: str,
        framework_control: str,
        initial_concern: str,
        max_tokens: int = 2048,
    ) -> dict:
        """Generate detailed finding information for a specific concern."""
        if not self.is_configured:
            raise ValueError("Google API key not configured")

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

        raw_text, _, _ = await self._generate(prompt, max_tokens=max_tokens)
        return self._parse_json_response(raw_text)

    async def answer_query(
        self,
        query: str,
        context_chunks: list[dict],
        max_tokens: int = 2048,
    ) -> dict:
        """Answer a natural language query about the documents."""
        if not self.is_configured:
            raise ValueError("Google API key not configured")

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

        raw_text, _, _ = await self._generate(prompt, max_tokens=max_tokens)
        return self._parse_json_response(raw_text)


LLMService = GeminiService


_gemini_service: GeminiService | None = None
_llm_service: LLMService | None = None


def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


def create_llm_service(provider: str | None = None) -> LLMService:
    settings = get_settings()
    provider = provider or settings.llm_provider
    if provider == "gemini":
        return GeminiService()
    raise ValueError(f"Unsupported LLM provider: {provider}. Only 'gemini' is supported.")


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = create_llm_service()
    return _llm_service


def reset_llm_service() -> None:
    global _llm_service
    _llm_service = None
