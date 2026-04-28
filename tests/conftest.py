from pathlib import Path
from dotenv import load_dotenv

from src.config import get_settings


def pytest_configure(config):
    root_path = Path(__file__).resolve().parents[1]

    get_settings.cache_clear()
    
    load_dotenv(root_path / ".env", override=False)
    load_dotenv(root_path / "tests/.env.test", override=True)

    get_settings.cache_clear()
