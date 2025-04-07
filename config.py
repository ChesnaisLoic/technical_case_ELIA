from pydantic_settings import BaseSettings, SettingsConfigDict


class Base(BaseSettings):

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Base()
