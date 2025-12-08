#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent Research System.

This system analyzes AI investments by major companies using a multi-agent
architecture with specialized agents for document location, company analysis,
and synthesis.
"""

import sys
import argparse
from typing import List, Optional

from config import Settings
from orchestrator import MultiAgentOrchestrator
from utils import get_logger


# Default companies to analyze
DEFAULT_COMPANIES = [
    "Oracle",
    "IBM",
    "Cisco",
    "SAP",
    "Walmart",
    "Salesforce"
]


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Research System for AI Investment Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default companies
  python main.py

  # Analyze specific companies
  python main.py --companies "Microsoft" "Google" "Amazon"

  # Custom output file
  python main.py --output my_analysis.md

  # Clear cache before running
  python main.py --clear-cache

  # Quiet mode (less verbose)
  python main.py --quiet

  # Clear cache only (don't run analysis)
  python main.py --clear-cache-only
        """
    )

    parser.add_argument(
        '--companies',
        nargs='+',
        help='List of companies to analyze (default: Oracle, IBM, Cisco, SAP, Walmart, Salesforce)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output filename for the report (default: auto-generated with timestamp)'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear cache before running analysis'
    )

    parser.add_argument(
        '--clear-cache-only',
        action='store_true',
        help='Clear cache and exit (do not run analysis)'
    )

    parser.add_argument(
        '--clear-expired-cache',
        action='store_true',
        help='Clear only expired cache entries'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        help='Anthropic API key (overrides .env file)'
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    logger = get_logger("Main")

    # Parse arguments
    args = parse_arguments()

    # Override settings if quiet mode
    if args.quiet:
        Settings.VERBOSE = False

    try:
        # Initialize orchestrator
        orchestrator = MultiAgentOrchestrator(api_key=args.api_key)

        # Handle cache operations
        if args.clear_cache_only:
            count = orchestrator.clear_cache()
            print(f"✓ Cleared {count} cache files")
            return 0

        if args.clear_expired_cache:
            count = orchestrator.clear_expired_cache()
            print(f"✓ Cleared {count} expired cache files")
            if not (args.companies or args.clear_cache):
                return 0

        if args.clear_cache:
            count = orchestrator.clear_cache()
            logger.info(f"Cleared {count} cache files")

        # Determine companies to analyze
        companies = args.companies if args.companies else DEFAULT_COMPANIES

        # Run analysis
        logger.info(f"Starting analysis for {len(companies)} companies")
        report_path = orchestrator.run_analysis(
            companies=companies,
            output_filename=args.output
        )

        # Success
        if not Settings.VERBOSE:
            print(f"\n✓ Analysis complete. Report saved to: {report_path}")

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        print("\nPlease check your .env file and ensure ANTHROPIC_API_KEY is set.", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\n\n⚠️  Analysis interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
