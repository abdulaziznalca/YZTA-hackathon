from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./shoppilot.db"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # WhatsApp / Twilio
    WHATSAPP_PROVIDER: str = "twilio"  # "twilio" | "meta"
    WHATSAPP_VERIFY_TOKEN: str = "shoppilot_verify"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"  # Twilio Sandbox default
    TWILIO_SKIP_SIGNATURE: bool = True  # set False in production

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
