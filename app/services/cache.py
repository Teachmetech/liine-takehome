import json
from typing import List, Optional
import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL)
CACHE_TTL = 3600  # 1 hour


def get_cached_restaurants(datetime_str: str) -> Optional[List[str]]:
    """Get restaurants from cache for given datetime"""
    try:
        cache_key = f"restaurants:{datetime_str}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {datetime_str}")
            return json.loads(cached_data)
        logger.debug(f"Cache miss for {datetime_str}")
        return None
    except Exception as e:
        logger.error(f"Error accessing cache: {str(e)}")
        return None


def set_cached_restaurants(datetime_str: str, restaurants: List[str]) -> None:
    """Cache restaurants for given datetime"""
    try:
        cache_key = f"restaurants:{datetime_str}"
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(restaurants))
        logger.debug(f"Cached {len(restaurants)} restaurants for {datetime_str}")
    except Exception as e:
        logger.error(f"Error setting cache: {str(e)}")


def invalidate_cache() -> None:
    """Clear all cached data"""
    try:
        redis_client.flushdb()
        logger.info("Cache invalidated")
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")
