"""Settings and configuration management."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    CACHE_DIR = BASE_DIR / os.getenv('CACHE_DIR', '.cache')
    OUTPUT_DIR = BASE_DIR / os.getenv('OUTPUT_DIR', 'reports')

    # API Configuration
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')

    # Model Configuration
    DEFAULT_MODEL: str = os.getenv('DEFAULT_MODEL', 'claude-sonnet-4-5-20250929')
    LEAD_AGENT_MODEL: str = os.getenv('LEAD_AGENT_MODEL', 'claude-haiku-4-5-20250929')
    SUB_AGENT_MODEL: str = os.getenv('SUB_AGENT_MODEL', 'claude-sonnet-4-5-20250929')
    SYNTHESIS_AGENT_MODEL: str = os.getenv('SYNTHESIS_AGENT_MODEL', 'claude-sonnet-4-5-20250929')

    # Token Limits (for cost optimization)
    MAX_TOKENS_LEAD_AGENT: int = int(os.getenv('MAX_TOKENS_LEAD_AGENT', '2000'))
    MAX_TOKENS_SUB_AGENT: int = int(os.getenv('MAX_TOKENS_SUB_AGENT', '3000'))
    MAX_TOKENS_SYNTHESIS: int = int(os.getenv('MAX_TOKENS_SYNTHESIS', '6000'))

    # Feature Flags
    ENABLE_CACHING: bool = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    PARALLEL_EXECUTION: bool = os.getenv('PARALLEL_EXECUTION', 'false').lower() == 'true'
    VERBOSE: bool = os.getenv('VERBOSE', 'true').lower() == 'true'

    # Rate Limiting
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY: int = int(os.getenv('RETRY_DELAY', '2'))

    @classmethod
    def validate(cls) -> bool:
        """Validate required settings."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set it in .env file or environment variables."
            )
        return True

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_model_for_agent(cls, agent_type: str) -> str:
        """Get the appropriate model for an agent type."""
        models = {
            'lead': cls.LEAD_AGENT_MODEL,
            'sub': cls.SUB_AGENT_MODEL,
            'synthesis': cls.SYNTHESIS_AGENT_MODEL,
        }
        return models.get(agent_type, cls.DEFAULT_MODEL)

    @classmethod
    def get_max_tokens_for_agent(cls, agent_type: str) -> int:
        """Get max tokens for an agent type."""
        tokens = {
            'lead': cls.MAX_TOKENS_LEAD_AGENT,
            'sub': cls.MAX_TOKENS_SUB_AGENT,
            'synthesis': cls.MAX_TOKENS_SYNTHESIS,
        }
        return tokens.get(agent_type, 4000)
