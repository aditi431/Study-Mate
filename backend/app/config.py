from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    app_name: str = "StudyMate API"
    environment: str = "development"
    database_url: str = Field(min_length=1)
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "CORS_ORIGINS"),
    )
    gemini_api_key: SecretStr | None = None
    ai_daily_limit_per_user: int = Field(default=20, ge=1)
    ai_rate_limit_per_minute: int = Field(default=10, ge=1)
    ai_request_timeout_seconds: float = Field(default=10, gt=0, le=60)
    demo_mode: bool = False
    demo_email: str = "demo@studymate.local"
    demo_password: SecretStr | None = None
    demo_ai_daily_limit_per_user: int = Field(default=3, ge=1)

    model_config = SettingsConfigDict(
        env_file=BACKEND_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def validate_runtime_settings(self):
        jwt_secret = self.jwt_secret.get_secret_value()
        if len(jwt_secret) < 32 or "replace-with" in jwt_secret.lower():
            raise ValueError(
                "JWT_SECRET must be a non-placeholder value of at least 32 characters"
            )
        if self.environment.lower() == "production":
            if self.database_url.lower().startswith("sqlite"):
                raise ValueError("DATABASE_URL must use MySQL or PostgreSQL in production")
        if self.demo_mode:
            if not self.demo_email.strip():
                raise ValueError("DEMO_EMAIL must be set when DEMO_MODE is enabled")
            demo_password = (
                self.demo_password.get_secret_value()
                if self.demo_password is not None
                else ""
            )
            if len(demo_password) < 12 or "replace-with" in demo_password.lower():
                raise ValueError(
                    "DEMO_PASSWORD must be a non-placeholder value of at least 12 characters "
                    "when DEMO_MODE is enabled"
                )
            if self.demo_ai_daily_limit_per_user >= self.ai_daily_limit_per_user:
                raise ValueError(
                    "DEMO_AI_DAILY_LIMIT_PER_USER must be lower than AI_DAILY_LIMIT_PER_USER"
                )
        return self

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        missing = sorted(
            {
                str(error["loc"][0]).upper()
                for error in exc.errors()
                if error["type"] == "missing"
            }
        )
        if missing:
            names = ", ".join(missing)
            raise RuntimeError(
                f"Missing required environment variable(s): {names}. "
                "Set them in backend/.env or in the process environment."
            ) from None
        issues = "; ".join(
            error["msg"] for error in exc.errors(include_input=False)
        )
        raise RuntimeError(
            f"Invalid application configuration: {issues}. "
            "Check backend/.env and the process environment variables."
        ) from None
