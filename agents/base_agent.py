"""Base agent class with common functionality."""

import time
import json
from typing import Optional, Dict, Any
import anthropic
from anthropic import RateLimitError

from config import Settings
from utils import get_logger, Cache


class BaseAgent:
    """Base class for all agents with common functionality."""

    def __init__(
        self,
        name: str,
        role: str,
        agent_type: str,
        client: anthropic.Anthropic,
        cache: Optional[Cache] = None
    ):
        """Initialize base agent.

        Args:
            name: Agent name
            role: Agent role description
            agent_type: Type of agent (lead, sub, synthesis)
            client: Anthropic client instance
            cache: Optional cache instance
        """
        self.name = name
        self.role = role
        self.agent_type = agent_type
        self.client = client
        self.cache = cache
        self.logger = get_logger(f"Agent.{name}")

        # Get model and token limits from settings
        self.model = Settings.get_model_for_agent(agent_type)
        self.max_tokens = Settings.get_max_tokens_for_agent(agent_type)

        self.logger.info(f"Initialized {name} (Type: {agent_type}, Model: {self.model})")

    def invoke(
        self,
        prompt: str,
        context: str = "",
        use_cache: bool = True,
        **kwargs
    ) -> tuple[str, int, int]:
        """Invoke the agent with a prompt.

        Args:
            prompt: The prompt to send to the agent
            context: Optional context to prepend to prompt
            use_cache: Whether to use caching
            **kwargs: Additional arguments for the API call

        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        # Check cache first
        if use_cache and self.cache and Settings.ENABLE_CACHING:
            cached_response = self.cache.get(
                agent_name=self.name,
                prompt=prompt,
                context=context
            )
            if cached_response:
                self.logger.info(f"{self.name}: Using cached response")
                return cached_response['text'], 0, 0

        # Prepare full prompt
        full_prompt = self._build_prompt(prompt, context)

        # Call API with retry logic
        response_text, input_tokens, output_tokens = self._call_api_with_retry(
            full_prompt,
            **kwargs
        )

        # Cache the response
        if use_cache and self.cache and Settings.ENABLE_CACHING:
            self.cache.set(
                {
                    'text': response_text,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens
                },
                agent_name=self.name,
                prompt=prompt,
                context=context
            )

        return response_text, input_tokens, output_tokens

    def _build_prompt(self, prompt: str, context: str = "") -> str:
        """Build the full prompt with role and context.

        Args:
            prompt: Main prompt
            context: Optional context

        Returns:
            Full prompt string
        """
        parts = [self.role]

        if context:
            parts.append(f"\nContext:\n{context}")

        parts.append(f"\nTask:\n{prompt}")

        return "\n\n".join(parts)

    def _call_api_with_retry(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> tuple[str, int, int]:
        """Call Anthropic API with retry logic.

        Args:
            prompt: Prompt to send
            max_retries: Maximum number of retries
            **kwargs: Additional API parameters

        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        max_retries = max_retries or Settings.MAX_RETRIES
        last_exception = None

        for attempt in range(max_retries):
            try:
                self.logger.debug(f"{self.name}: API call attempt {attempt + 1}/{max_retries}")

                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=kwargs.get('max_tokens', self.max_tokens),
                    messages=[{"role": "user", "content": prompt}],
                    **{k: v for k, v in kwargs.items() if k != 'max_tokens'}
                )

                response_text = message.content[0].text

                # Extract token usage
                input_tokens = message.usage.input_tokens
                output_tokens = message.usage.output_tokens

                self.logger.debug(
                    f"{self.name}: Tokens - Input: {input_tokens}, Output: {output_tokens}"
                )

                return response_text, input_tokens, output_tokens

            except RateLimitError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = Settings.RETRY_DELAY * (attempt + 1)
                    self.logger.warning(
                        f"{self.name}: Rate limited. Waiting {wait_time}s before retry..."
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"{self.name}: Max retries exceeded")
                    raise

            except Exception as e:
                self.logger.error(f"{self.name}: API call failed: {str(e)}")
                raise

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError(f"{self.name}: Failed to get API response")

    def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text response.

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON dictionary or None
        """
        try:
            # Try direct parsing
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        # Try to find JSON array
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        self.logger.warning(f"{self.name}: Could not extract JSON from response")
        return None
