from flask_caching import Cache
import os

cache_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
    "CACHE_REDIS_PORT": os.getenv("REDIS_PORT", 6379),
    "CACHE_REDIS_DB": 0,
    "CACHE_REDIS_URL": f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    "CACHE_DEFAULT_TIMEOUT": 300  # 5 minutes cache timeout
}

cache = Cache(config=cache_config)

def init_cache(app):
    """Initialize cache with Flask app"""
    cache.init_app(app)
