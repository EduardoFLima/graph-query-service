from functools import lru_cache

from pydantic import computed_field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseModel):
    postgres_db: str = ""
    postgres_password: str = ""

    @computed_field
    @property
    def db_uri(self) -> str:
        return f"postgresql://postgres:{self.postgres_password}@localhost:5432/{self.postgres_db}"

class Neo4jSettings(BaseModel):
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""

class SafeguardSettings(BaseModel):

    enabled: bool = True
    model: str = "openai/gpt-oss-safeguard-20b"


class Settings(BaseSettings):
    openrouter_api_key: str
    langsmith_api_key: str

    models: list[str] = [
        "meta-llama/llama-3.1-8b-instruct",
        "openai/gpt-oss-20b",
        "nvidia/nemotron-3-super-120b-a12b:free"
    ]

    http_referer: str = "some.web.site"
    x_title: str = "Testing chat agent"
    provider: dict = dict(sort=dict(by="throughput", partition="none"))
    temperature: float = 0.2

    memory: PostgresSettings = PostgresSettings()
    graph_db: Neo4jSettings = Neo4jSettings()
    safeguard: SafeguardSettings = SafeguardSettings()

    # loading .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__")


@lru_cache
def get_settings() -> Settings:
    return Settings()
