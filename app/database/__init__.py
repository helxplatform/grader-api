import redis.asyncio as aioredis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis
from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

redis_general_client = Redis.from_url(settings.REDIS_GENERAL_DATABASE_URI, health_check_interval=30)
redis_general_async_client = aioredis.Redis.from_url(settings.REDIS_GENERAL_DATABASE_URI, health_check_interval=30)
redis_broker_client = Redis.from_url(settings.CELERY_BROKER_URI, health_check_interval=30)
# Currently not used, so no need to create a connection pool and client for it.
# redis_result_backend_client = Redis.from_url(settings.CELERY_RESULT_BACKEND_URI)