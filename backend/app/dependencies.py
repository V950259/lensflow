from .core.ai_client import LensAI
from .core.logic_engine import LogicEngine
from .core.history_manager import HistoryManager
from .core.cache_manager import AsyncCacheManager
from .core.local_processor import LocalProcessor
import os
from functools import lru_cache
from fastapi import Header, Depends

@lru_cache()
def get_ai_client(x_api_key: str = Header(None, alias="X-API-Key")):
    # Retrieve API key from environment variables as fallback
    api_key = x_api_key or os.getenv("API_KEY", "9e546f3625334bfc9ea8a55036680de1.GtUkOzGH57D4IU3l")
    base_url = os.getenv("API_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
    model_name = os.getenv("MODEL_NAME", "glm-4v")
    # Note: We are creating a new instance if api_key changes, but lru_cache might not handle this well if we want per-request key.
    # However, for simplicity in this contest project, we will return a new instance or cached one.
    # Actually, lru_cache keys on arguments. If x_api_key is None, it uses env. If provided, it uses that.
    return LensAI(api_key=api_key, base_url=base_url, model_name=model_name)

@lru_cache()
def get_logic_engine():
    # Ensure data path is correct relative to working directory
    # In Docker, WORKDIR is /app, data is mounted at /app/data
    return LogicEngine() 

@lru_cache()
def get_history_manager():
    return HistoryManager(db_path="data/history.db")

# Cache manager singleton
cache_manager_instance = AsyncCacheManager()
def get_cache_manager():
    return cache_manager_instance

# Local processor singleton
local_processor_instance = LocalProcessor()
def get_local_processor():
    return local_processor_instance
