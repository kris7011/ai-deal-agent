import os
from dotenv import load_dotenv


def get_cors_origins() -> list[str]:
    load_dotenv(override=True)

    origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    return [origin.strip() for origin in origins.split(",") if origin.strip()]
