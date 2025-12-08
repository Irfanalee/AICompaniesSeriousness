"""Synthesis agent for creating comprehensive cross-company reports."""

from typing import List, Optional
import anthropic
import json

from .base_agent import BaseAgent
from .company_analysis_agent import CompanyAnalysis
from utils import Cache


class SynthesisAgent(BaseAgent):
    """Agent responsible for synthesizing results into comprehensive reports."""

    def __init__(self, client: anthropic.Anthropic, cache: Optional[Cache] = None):
        """Initialize synthesis agent.

        Args:
            client: Anthropic client instance
            cache: Optional cache instance
        """
        role = """You are a synthesis agent responsible for creating comprehensive financial analysis reports.

Your tasks:
1. Compare data across companies
2. Create clear comparison tables in markdown
3. Identify patterns and trends
4. Generate actionable insights
5. Provide executive summaries

Output well-formatted markdown with clear structure and insights."""

        super().__init__(
            name="SynthesisAgent",
            role=role,
            agent_type="synthesis",
            client=client,
            cache=cache
        )

    def create_report(
        self,
        analyses: List[CompanyAnalysis]
    ) -> tuple[str, int, int]:
        """Create comprehensive analysis report.

        Args:
            analyses: List of CompanyAnalysis objects

        Returns:
            Tuple of (markdown report, input_tokens, output_tokens)
        """
        self.logger.info(f"Creating synthesis report for {len(analyses)} companies")

        # Prepare data summary for the synthesis agent
        company_data = []
        for analysis in analyses:
            company_data.append({
                "company": analysis.company,
                "gen_ai_mentions": analysis.gen_ai_mentions,
                "ml_mentions": analysis.ml_mentions,
                "total_mentions": analysis.gen_ai_mentions + analysis.ml_mentions,
                "capex_ai": analysis.capex_ai,
                "cfo_quote": analysis.cfo_quote,
                "insights": analysis.key_insights
            })

        # Sort by total mentions (descending)
        company_data.sort(key=lambda x: x['total_mentions'], reverse=True)

        context = f"Company Analysis Data:\n{json.dumps(company_data, indent=2)}"

        prompt = """Create a comprehensive "Talk vs Walk" analysis report for AI investments.

Structure:

# AI Investment Analysis: Talk vs Walk

## Executive Summary
(3-4 sentences summarizing key findings)

## Talk vs Walk Comparison Table

| Company | Gen AI Mentions | ML Mentions | Total "Talk" | AI CapEx "Walk" | Talk/Walk Analysis |
|---------|-----------------|-------------|--------------|-----------------|-------------------|
| ...     | ...             | ...         | ...          | ...             | ...               |

Sort by Total "Talk" (descending).

## Key Findings

- Which companies are investing most heavily?
- Which companies show high rhetoric but low disclosed investment?
- Which have clearest ROI timelines?

## CFO/CEO Perspectives on ROI

Summarize each company's leadership stance on AI investment returns and timelines.

## Investment Patterns

Identify trends:
- Infrastructure vs application spending
- Disclosure transparency levels
- Timeline confidence levels
- Sector differences (tech vs retail)

## Conclusions and Recommendations

### For Investors
(3-5 bullet points)

### For Enterprises
(3-5 bullet points)

### Overall Assessment
(2-3 paragraphs)

---

Use clear markdown formatting. Make tables align properly. Be specific and cite numbers."""

        # Invoke synthesis agent
        response_text, input_tokens, output_tokens = self.invoke(
            prompt=prompt,
            context=context,
            use_cache=False  # Don't cache synthesis as it's the final output
        )

        self.logger.info("Synthesis report created successfully")

        return response_text, input_tokens, output_tokens
