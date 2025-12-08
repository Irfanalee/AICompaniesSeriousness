"""Lead agent for document location and orchestration."""

from typing import List, Dict, Any, Optional
import anthropic

from .base_agent import BaseAgent
from utils import Cache


class LeadAgent(BaseAgent):
    """Lead agent responsible for locating documents and orchestrating the workflow."""

    def __init__(self, client: anthropic.Anthropic, cache: Optional[Cache] = None):
        """Initialize lead agent.

        Args:
            client: Anthropic client instance
            cache: Optional cache instance
        """
        role = """You are a lead financial research agent responsible for locating company documents.

Your tasks:
1. Identify the most recent fiscal year for each company
2. Provide SEC EDGAR URLs for 10-K filings
3. Provide investor relations URLs
4. Provide earnings call transcript URLs if available

IMPORTANT: Output ONLY valid JSON. No markdown, no explanations."""

        super().__init__(
            name="LeadDocumentLocator",
            role=role,
            agent_type="lead",
            client=client,
            cache=cache
        )

    def locate_documents(self, companies: List[str]) -> List[Dict[str, Any]]:
        """Locate documents for all companies.

        Args:
            companies: List of company names

        Returns:
            List of dictionaries with document locations for each company
        """
        self.logger.info(f"Locating documents for {len(companies)} companies")

        prompt = f"""Locate the most recent 10-K filings and earnings call transcripts for these companies:
{', '.join(companies)}

For EACH company, provide:
1. Company name (exactly as provided)
2. Stock ticker symbol
3. Most recent fiscal year end date (YYYY-MM-DD)
4. SEC EDGAR URL for 10-K filing
5. Investor relations URL
6. Earnings call transcript URL (if available)

Return as a JSON array with this EXACT structure:
[
  {{
    "company": "Oracle",
    "ticker": "ORCL",
    "fiscal_year_end": "2024-05-31",
    "tenk_url": "https://www.sec.gov/...",
    "investor_relations_url": "https://...",
    "earnings_transcript_url": "https://..."
  }}
]

Output ONLY the JSON array, nothing else."""

        response_text, input_tokens, output_tokens = self.invoke(
            prompt=prompt,
            use_cache=True
        )

        # Parse JSON response
        document_locations = self.extract_json(response_text)

        if document_locations is None:
            self.logger.error("Failed to parse document locations from response")
            # Return default structure
            document_locations = [
                {
                    "company": company,
                    "ticker": "N/A",
                    "fiscal_year_end": "2024",
                    "tenk_url": f"https://www.sec.gov/cgi-bin/browse-edgar?company={company}",
                    "investor_relations_url": "N/A",
                    "earnings_transcript_url": "N/A"
                }
                for company in companies
            ]

        self.logger.info(f"Located documents for {len(document_locations)} companies")
        return document_locations, input_tokens, output_tokens
