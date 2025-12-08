"""Company analysis sub-agent for individual company analysis."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import anthropic

from .base_agent import BaseAgent
from utils import Cache


@dataclass
class CompanyAnalysis:
    """Results from analyzing a single company."""
    company: str
    gen_ai_mentions: int
    ml_mentions: int
    capex_ai: str
    cfo_quote: str
    key_insights: str
    documents_analyzed: list


class CompanyAnalysisAgent(BaseAgent):
    """Sub-agent responsible for analyzing a single company's documents."""

    def __init__(
        self,
        company: str,
        client: anthropic.Anthropic,
        cache: Optional[Cache] = None
    ):
        """Initialize company analysis agent.

        Args:
            company: Company name to analyze
            client: Anthropic client instance
            cache: Optional cache instance
        """
        role = f"""You are an expert financial analyst specializing in {company}.

Your tasks:
1. Count mentions of "Generative AI", "Gen AI", "GenAI" and similar terms
2. Count mentions of "Machine Learning", "ML" and similar terms
3. Extract specific Capital Expenditure (CapEx) numbers attributed to AI infrastructure
4. Find ONE quote from CFO or CEO about ROI timeline for AI investments

Be precise and cite specific numbers. Output ONLY valid JSON, no markdown."""

        super().__init__(
            name=f"{company}Analyst",
            role=role,
            agent_type="sub",
            client=client,
            cache=cache
        )
        self.company = company

    def analyze_documents(
        self,
        document_urls: Dict[str, str],
        document_content: Optional[str] = None
    ) -> tuple[CompanyAnalysis, int, int]:
        """Analyze company documents.

        Args:
            document_urls: Dictionary with document URLs
            document_content: Optional actual document content

        Returns:
            Tuple of (CompanyAnalysis object, input_tokens, output_tokens)
        """
        self.logger.info(f"Analyzing documents for {self.company}")

        # Build context
        context_parts = [f"Analyzing: {self.company}"]
        if document_urls:
            context_parts.append("Document sources:")
            for key, url in document_urls.items():
                if url and url != "N/A":
                    context_parts.append(f"  - {key}: {url}")

        context = "\n".join(context_parts)

        # Build prompt
        if document_content:
            # If actual content provided, analyze it
            prompt = f"""Analyze the following document content for {self.company}:

{document_content[:30000]}

Tasks:
1. Count ALL mentions of "Generative AI", "Gen AI", "GenAI" (case-insensitive) - exact count
2. Count ALL mentions of "Machine Learning", "ML", "artificial intelligence" (case-insensitive) - exact count
3. Extract SPECIFIC CapEx dollar amounts for AI infrastructure (GPUs, data centers, etc.)
4. Find ONE direct quote from CFO/CEO about AI ROI timeline

Output as JSON:
{{
  "gen_ai_mentions": <number>,
  "ml_mentions": <number>,
  "capex_ai": "<specific amount or 'Not explicitly disclosed'>",
  "cfo_quote": "<exact quote or 'No specific timeline quote found'>",
  "key_insights": "<2-3 sentence summary>"
}}"""
        else:
            # Use knowledge-based analysis
            prompt = f"""Based on your knowledge of {self.company}'s recent public filings and statements:

Tasks:
1. Estimate mentions of "Generative AI" / "Gen AI" terminology in recent 10-Ks and earnings calls
2. Estimate mentions of "Machine Learning" / "ML" terminology
3. Identify any disclosed AI-specific CapEx or infrastructure spending
4. Recall any CFO/CEO quotes about AI investment ROI timelines

NOTE: This is based on training data, not live documents.

Output as JSON:
{{
  "gen_ai_mentions": <estimated number>,
  "ml_mentions": <estimated number>,
  "capex_ai": "<amount if known or 'Not disclosed / Unknown'>",
  "cfo_quote": "<quote if recalled or 'No specific quote available'>",
  "key_insights": "<summary of AI strategy based on knowledge>"
}}"""

        # Invoke agent
        response_text, input_tokens, output_tokens = self.invoke(
            prompt=prompt,
            context=context,
            use_cache=True
        )

        # Parse response
        data = self.extract_json(response_text)

        if data is None:
            self.logger.error(f"Failed to parse analysis for {self.company}")
            data = {
                "gen_ai_mentions": 0,
                "ml_mentions": 0,
                "capex_ai": "Error in analysis",
                "cfo_quote": "Error in analysis",
                "key_insights": "Analysis failed"
            }

        # Create CompanyAnalysis object
        analysis = CompanyAnalysis(
            company=self.company,
            gen_ai_mentions=data.get('gen_ai_mentions', 0),
            ml_mentions=data.get('ml_mentions', 0),
            capex_ai=data.get('capex_ai', 'Not disclosed'),
            cfo_quote=data.get('cfo_quote', 'No quote found'),
            key_insights=data.get('key_insights', ''),
            documents_analyzed=[
                document_urls.get('tenk_url', ''),
                document_urls.get('earnings_transcript_url', '')
            ]
        )

        self.logger.info(
            f"Analysis complete for {self.company}: "
            f"Gen AI: {analysis.gen_ai_mentions}, ML: {analysis.ml_mentions}"
        )

        return analysis, input_tokens, output_tokens
