"""Make one real, secret-safe Gemini structured-output smoke request.

Exit codes:
    0: Provider returned a valid structured response.
    2: Provider is not configured.
    3: Required local dependency is unavailable.
    4: Provider request or response validation failed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "gemini-3.5-flash-lite"


def _load_local_environment() -> None:
    """Load backend/.env when python-dotenv is available.

    Missing python-dotenv is not fatal when variables already come from the
    process environment. The script reports the missing Gemini SDK separately.
    """

    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv(BACKEND_DIR / ".env", override=False)


def _safe_error_category(exc: Exception) -> str:
    """Return a useful category without echoing provider bodies or secrets."""

    status_code = getattr(exc, "status_code", None)
    if status_code in {401, 403}:
        return "authentication-or-permission"
    if status_code == 429:
        return "rate-limit-or-quota"
    if status_code == 404:
        return "model-not-found"
    if isinstance(exc, TimeoutError):
        return "timeout"
    return type(exc).__name__


def main() -> int:
    _load_local_environment()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

    if not api_key:
        print(
            "AI_SMOKE status=UNAVAILABLE provider=gemini "
            f"model={model} reason=missing-api-key"
        )
        return 2

    try:
        from google import genai
        from google.genai import types
        from pydantic import BaseModel, ConfigDict
    except ImportError:
        print(
            "AI_SMOKE status=UNAVAILABLE provider=gemini "
            f"model={model} reason=missing-google-genai-sdk"
        )
        return 3

    class SmokeResponse(BaseModel):
        model_config = ConfigDict(extra="forbid")

        status: str

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=(
                "Return a JSON object with exactly one field named status and "
                "set its value to READY. Do not include any other fields."
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SmokeResponse,
                temperature=0,
            ),
        )
        parsed = SmokeResponse.model_validate_json(response.text)
        if parsed.status != "READY":
            raise ValueError("unexpected-structured-status")
    except Exception as exc:  # Provider SDK exposes multiple transport errors.
        category = _safe_error_category(exc)
        print(
            "AI_SMOKE status=UNAVAILABLE provider=gemini "
            f"model={model} reason={category}"
        )
        return 4

    print(f"AI_SMOKE status=AVAILABLE provider=gemini model={model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

