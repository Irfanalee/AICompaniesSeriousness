"""Main orchestrator for the multi-agent research system."""

from typing import List, Optional
from pathlib import Path
from datetime import datetime
import anthropic

from config import Settings
from utils import Cache, get_logger, TokenCounter
from agents import LeadAgent, CompanyAnalysisAgent, SynthesisAgent, CompanyAnalysis


class MultiAgentOrchestrator:
    """Orchestrator for coordinating multiple agents in the research system."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the orchestrator.

        Args:
            api_key: Optional Anthropic API key (uses Settings if not provided)
        """
        # Validate settings
        if api_key:
            Settings.ANTHROPIC_API_KEY = api_key
        Settings.validate()
        Settings.ensure_directories()

        # Initialize client
        self.client = anthropic.Anthropic(api_key=Settings.ANTHROPIC_API_KEY)

        # Initialize cache
        self.cache = Cache(Settings.CACHE_DIR) if Settings.ENABLE_CACHING else None

        # Initialize token counter
        self.token_counter = TokenCounter()

        # Initialize logger
        self.logger = get_logger("Orchestrator")

        # Track models used
        self.models_used = {}

        self.logger.info("Multi-Agent Orchestrator initialized")
        self.logger.info(f"Caching: {'Enabled' if Settings.ENABLE_CACHING else 'Disabled'}")
        self.logger.info(f"Parallel Execution: {'Enabled' if Settings.PARALLEL_EXECUTION else 'Disabled'}")

    def run_analysis(
        self,
        companies: List[str],
        output_filename: Optional[str] = None
    ) -> str:
        """Run complete multi-agent analysis.

        Args:
            companies: List of company names to analyze
            output_filename: Optional custom output filename

        Returns:
            Path to generated report file
        """
        if Settings.VERBOSE:
            self._print_header()

        start_time = datetime.now()

        # Phase 1: Document Location
        if Settings.VERBOSE:
            self._print_phase_header(1, "Document Location")

        document_locations, lead_input, lead_output = self._phase_1_locate_documents(companies)

        # Track tokens
        self.models_used['LeadAgent'] = Settings.LEAD_AGENT_MODEL
        self.token_counter.track('LeadAgent', Settings.LEAD_AGENT_MODEL, lead_input, lead_output)

        # Phase 2: Company Analysis
        if Settings.VERBOSE:
            self._print_phase_header(2, "Company Analysis")

        analyses = self._phase_2_analyze_companies(document_locations)

        # Phase 3: Synthesis
        if Settings.VERBOSE:
            self._print_phase_header(3, "Report Synthesis")

        report, synth_input, synth_output = self._phase_3_synthesize(analyses)

        # Track synthesis tokens
        self.models_used['SynthesisAgent'] = Settings.SYNTHESIS_AGENT_MODEL
        self.token_counter.track('SynthesisAgent', Settings.SYNTHESIS_AGENT_MODEL, synth_input, synth_output)

        # Save report
        report_path = self._save_report(report, output_filename)

        # Print summary
        if Settings.VERBOSE:
            elapsed = (datetime.now() - start_time).total_seconds()
            self._print_completion(report_path, elapsed)
            self.token_counter.print_summary(self.models_used)

        return str(report_path)

    def _phase_1_locate_documents(self, companies: List[str]) -> tuple:
        """Phase 1: Locate documents using lead agent."""
        self.logger.info(f"Phase 1: Locating documents for {len(companies)} companies")

        lead_agent = LeadAgent(self.client, self.cache)
        document_locations, input_tokens, output_tokens = lead_agent.locate_documents(companies)

        if Settings.VERBOSE:
            print(f"  ✓ Located documents for {len(document_locations)} companies")

        return document_locations, input_tokens, output_tokens

    def _phase_2_analyze_companies(self, document_locations: List[dict]) -> List[CompanyAnalysis]:
        """Phase 2: Analyze each company with sub-agents."""
        self.logger.info(f"Phase 2: Analyzing {len(document_locations)} companies")

        analyses = []

        for i, doc_info in enumerate(document_locations):
            company = doc_info['company']

            if Settings.VERBOSE:
                print(f"\n  [{i+1}/{len(document_locations)}] Analyzing {company}...")

            # Create company-specific agent
            agent = CompanyAnalysisAgent(company, self.client, self.cache)

            # Analyze
            analysis, input_tokens, output_tokens = agent.analyze_documents(doc_info)
            analyses.append(analysis)

            # Track tokens
            agent_name = f"{company}Analyst"
            self.models_used[agent_name] = Settings.SUB_AGENT_MODEL
            self.token_counter.track(agent_name, Settings.SUB_AGENT_MODEL, input_tokens, output_tokens)

            if Settings.VERBOSE:
                print(f"      • Gen AI mentions: {analysis.gen_ai_mentions}")
                print(f"      • ML mentions: {analysis.ml_mentions}")
                capex_preview = analysis.capex_ai[:60] + "..." if len(analysis.capex_ai) > 60 else analysis.capex_ai
                print(f"      • AI CapEx: {capex_preview}")

        return analyses

    def _phase_3_synthesize(self, analyses: List[CompanyAnalysis]) -> tuple:
        """Phase 3: Synthesize results into final report."""
        self.logger.info("Phase 3: Synthesizing results")

        synthesis_agent = SynthesisAgent(self.client, self.cache)
        report, input_tokens, output_tokens = synthesis_agent.create_report(analyses)

        if Settings.VERBOSE:
            print("  ✓ Report synthesis complete")

        return report, input_tokens, output_tokens

    def _save_report(self, report: str, output_filename: Optional[str] = None) -> Path:
        """Save report to file."""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ai_investment_analysis_{timestamp}.md"

        output_path = Settings.OUTPUT_DIR / output_filename

        # Add metadata header
        metadata = f"""---
title: AI Investment Analysis - Talk vs Walk
generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
analysis_type: Multi-Agent Research System
---

"""
        full_report = metadata + report

        with open(output_path, 'w') as f:
            f.write(full_report)

        self.logger.info(f"Report saved to: {output_path}")
        return output_path

    def _print_header(self):
        """Print analysis header."""
        print("\n" + "=" * 80)
        print("MULTI-AGENT RESEARCH SYSTEM")
        print("AI Investment Analysis: Talk vs Walk")
        print("=" * 80)

    def _print_phase_header(self, phase_num: int, phase_name: str):
        """Print phase header."""
        print(f"\n[PHASE {phase_num}] {phase_name}")
        print("-" * 80)

    def _print_completion(self, report_path: Path, elapsed_seconds: float):
        """Print completion message."""
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\n✓ Report saved to: {report_path}")
        print(f"✓ Time elapsed: {elapsed_seconds:.1f} seconds")

    def clear_cache(self) -> int:
        """Clear all cached data.

        Returns:
            Number of cache files deleted
        """
        if self.cache:
            count = self.cache.clear()
            self.logger.info(f"Cleared {count} cache files")
            return count
        return 0

    def clear_expired_cache(self) -> int:
        """Clear expired cache entries.

        Returns:
            Number of cache files deleted
        """
        if self.cache:
            count = self.cache.clear_expired()
            self.logger.info(f"Cleared {count} expired cache files")
            return count
        return 0
