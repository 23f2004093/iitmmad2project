from flask_sqlalchemy import SQLAlchemy

import redis

from config import Config



db = SQLAlchemy()



redis_client = redis.Redis(

    host=Config.REDIS_HOST,

    port=Config.REDIS_PORT,

    decode_responses=True

)
