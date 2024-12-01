from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Cloud APP"
    APP_VERSION: str = "0.1.0"
    APP_ENVIRONMENT: str = "dev"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    BACKEND_URL: str = "http://localhost:9000"

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "cloud_db"
    DB_DRIVER: str = "postgresql+psycopg2"
    DB_URL_SOCKET: str = ""

    DB_USER_TEST: str = "postgres"
    DB_PASSWORD_TEST: str = "postgres"
    DB_HOST_TEST: str = "localhost"
    DB_PORT_TEST: int = 5432
    DB_NAME_TEST: str = "cloud_db_test"
    DB_DRIVER_TEST: str = "postgresql+psycopg2"

    CELERY_BROKER_HOST: str = "localhost"
    CELERY_BROKER_PORT: int = 6379

    PUBSUB_TOPIC_ID: str = "videos"
    PUBSUB_SUBSCRIPTION_ID: str = "videos-sub"

    GCP_PROJECT_ID: str = ""
    GCP_CREDENTIALS_BASE64: str = ""

    VIDEOS_BUCKET: str = "videos-api"

    SECRET_KEY: str = "mysecret"

    @property
    def DB_URL(self) -> str:
        if self.DB_URL_SOCKET:
            return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@/{self.DB_NAME}?host=={self.DB_URL_SOCKET}"
        else:
            return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_URL_TEST(self) -> str:
        return f"{self.DB_DRIVER_TEST}://{self.DB_USER_TEST}:{self.DB_PASSWORD_TEST}@{self.DB_HOST_TEST}:{self.DB_PORT_TEST}/{self.DB_NAME_TEST}"

    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.CELERY_BROKER_HOST}:{self.CELERY_BROKER_PORT}/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings: Settings = Settings()
