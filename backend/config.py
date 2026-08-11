import os



class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'portal.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = "redis://localhost:6379/0"

    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    REDIS_HOST = "localhost"

    REDIS_PORT = 6379
