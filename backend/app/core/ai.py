"""Evidence-bound AI proposal generation; this module never executes actions."""

from __future__ import annotations

import json

from google import genai
from google.genai import types

from app.config import Settings
from app.schemas import RootCauseProposal


class AIUnavailableError(RuntimeError):
    pass


def _gemini_schema(model: type[RootCauseProposal]) -> dict:
    """Gemini's schema dialect does not accept JSON Schema additionalProperties."""
    schema = model.model_json_schema()
    def clean(value):
        if isinstance(value, dict):
            value.pop("additionalProperties", None)
            for child in value.values(): clean(child)
        elif isinstance(value, list):
            for child in value: clean(child)
    clean(schema)
    return schema


def propose_recovery(settings: Settings, evidence: dict) -> RootCauseProposal:
    """Ask the configured model for a schema-valid allowlisted proposal."""
    if settings.ai_provider != "gemini":
        raise AIUnavailableError("Configured AI provider is not available in this build.")
    if not settings.provider_is_configured():
        raise AIUnavailableError("Gemini is not configured.")
    api_key = settings.gemini_api_key.get_secret_value()  # checked above
    client = genai.Client(api_key=api_key)
    prompt = (
        "Analyze this synthetic workflow incident. Propose exactly one correction. "
        "The only permitted action is RELEASE_RESERVATION and it must target the "
        "duplicate reservation ID present in evidence. Never propose code, SQL, shell, "
        "network calls, or automatic execution. Return only the requested schema.\n" +
        json.dumps(evidence, sort_keys=True)
    )
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_gemini_schema(RootCauseProposal),
            temperature=0,
        ),
    )
    if response.parsed is not None:
        return RootCauseProposal.model_validate(response.parsed)
    if not response.text:
        raise AIUnavailableError("Gemini returned no structured proposal.")
    return RootCauseProposal.model_validate_json(response.text)
