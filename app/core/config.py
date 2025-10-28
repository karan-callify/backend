from pydantic_settings import BaseSettings, SettingsConfigDict



_base_config = SettingsConfigDict(
    env_file=".env",             
    env_file_encoding="utf-8",
    env_ignore_empty=True,
    extra="ignore"
)

class AppSettings(BaseSettings):
    APP_NAME: str = "Callify"
    APP_DOMAIN: str = "localhost:8000"

    model_config = _base_config

class ApiKeysSettings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-mini"

    model_config = _base_config

class ExternalServiceSettings(BaseSettings):
    DOC_EXTRACT_API_URL: str
    model_config = _base_config

class DatabaseSettings(BaseSettings):    
    MONGO_URI: str 
    MONGO_DB_NAME: str

    model_config = _base_config


# These will now be filled by env vars or Docker Compose .env
app_settings = AppSettings()
api_keys_settings = ApiKeysSettings() # type: ignore
external_service_settings = ExternalServiceSettings() # type: ignore

db_settings = DatabaseSettings() # type: ignore



