"""Token counting and cost estimation utilities."""

from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    """Track token usage for cost estimation."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def add(self, input_tokens: int, output_tokens: int) -> None:
        """Add token usage."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += (input_tokens + output_tokens)


@dataclass
class TokenCounter:
    """Track and estimate costs for API usage."""

    # Token usage by agent type
    usage_by_agent: Dict[str, TokenUsage] = field(default_factory=dict)
    total_usage: TokenUsage = field(default_factory=TokenUsage)

    # Pricing (per million tokens) - Claude Sonnet 4.5 as of Dec 2024
    # Update these based on current Anthropic pricing
    PRICING = {
        'claude-opus-4-5-20251101': {'input': 15.00, 'output': 75.00},
        'claude-sonnet-4-5-20250929': {'input': 3.00, 'output': 15.00},
        'claude-haiku-4-5-20250929': {'input': 0.80, 'output': 4.00},
    }

    def track(self, agent_name: str, model: str, input_tokens: int, output_tokens: int) -> None:
        """Track token usage for an agent.

        Args:
            agent_name: Name of the agent
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        """
        if agent_name not in self.usage_by_agent:
            self.usage_by_agent[agent_name] = TokenUsage()

        self.usage_by_agent[agent_name].add(input_tokens, output_tokens)
        self.total_usage.add(input_tokens, output_tokens)

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        if model not in self.PRICING:
            # Default to Sonnet pricing
            model = 'claude-sonnet-4-5-20250929'

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost

    def get_total_cost_estimate(self, models_used: Dict[str, str]) -> float:
        """Get total estimated cost.

        Args:
            models_used: Mapping of agent names to models used

        Returns:
            Total estimated cost in USD
        """
        total_cost = 0.0

        for agent_name, usage in self.usage_by_agent.items():
            model = models_used.get(agent_name, 'claude-sonnet-4-5-20250929')
            cost = self.estimate_cost(model, usage.input_tokens, usage.output_tokens)
            total_cost += cost

        return total_cost

    def get_summary(self) -> Dict:
        """Get usage summary.

        Returns:
            Dictionary with usage statistics
        """
        return {
            'total_input_tokens': self.total_usage.input_tokens,
            'total_output_tokens': self.total_usage.output_tokens,
            'total_tokens': self.total_usage.total_tokens,
            'agents': {
                name: {
                    'input_tokens': usage.input_tokens,
                    'output_tokens': usage.output_tokens,
                    'total_tokens': usage.total_tokens
                }
                for name, usage in self.usage_by_agent.items()
            }
        }

    def print_summary(self, models_used: Dict[str, str]) -> None:
        """Print usage summary to console."""
        print("\n" + "=" * 60)
        print("TOKEN USAGE SUMMARY")
        print("=" * 60)

        print(f"\nTotal Tokens: {self.total_usage.total_tokens:,}")
        print(f"  Input:  {self.total_usage.input_tokens:,}")
        print(f"  Output: {self.total_usage.output_tokens:,}")

        print("\nBy Agent:")
        for agent_name, usage in self.usage_by_agent.items():
            print(f"  {agent_name}:")
            print(f"    Input:  {usage.input_tokens:,}")
            print(f"    Output: {usage.output_tokens:,}")
            print(f"    Total:  {usage.total_tokens:,}")

        total_cost = self.get_total_cost_estimate(models_used)
        print(f"\nEstimated Cost: ${total_cost:.4f}")
        print("=" * 60 + "\n")
