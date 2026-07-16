from flask_sqlalchemy import SQLAlchemy
import redis
from config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Redis client for sessions and caching
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True  # Decodes database bytes to standard strings
)