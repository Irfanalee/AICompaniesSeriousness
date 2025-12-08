"""Caching utilities for cost optimization."""

import json
import hashlib
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta


class Cache:
    """Simple file-based cache for agent responses."""

    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours for cache entries
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path for cache file."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, *args, **kwargs) -> Optional[Any]:
        """Retrieve cached value if available and not expired."""
        cache_key = self._get_cache_key(*args, **kwargs)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)

            # Check expiry
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                cache_path.unlink()  # Delete expired cache
                return None

            return cache_data['value']

        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def set(self, value: Any, *args, **kwargs) -> None:
        """Store value in cache."""
        cache_key = self._get_cache_key(*args, **kwargs)
        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }

        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def clear(self) -> int:
        """Clear all cache files. Returns number of files deleted."""
        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
            count += 1
        return count

    def clear_expired(self) -> int:
        """Clear expired cache entries. Returns number of files deleted."""
        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, ValueError):
                cache_file.unlink()
                count += 1
        return count
