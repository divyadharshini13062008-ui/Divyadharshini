import json
from typing import Any

from google import genai
from google.genai import types

from app.config import settings


SYSTEM_PROMPT = """
You are PocketSmart AI, a budget-aware recommendation assistant.

Return ONLY valid JSON.

The JSON must have this structure:

{
  "summary": "short summary",
  "tips": [
    "tip 1",
    "tip 2"
  ],
  "items": [
    {
      "name": "item name",
      "category": "category",
      "price": 0,
      "description": "description",
      "reason": "why this item fits",
      "source": "source",
      "url": "url"
    }
  ]
}

Rules:

- Respect the user's budget.
- Do not invent real-time availability.
- Do not claim that an item is currently in stock.
- Keep recommendations practical.
- Prefer affordable options.
- Prices are estimates unless supplied as catalog data.
"""


class GeminiService:

    def __init__(self):
        self.client = None

        if (
            not settings.use_mock_ai
            and settings.gemini_api_key
        ):
            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    def generate(
        self,
        prompt: str,
        image_bytes: bytes | None = None,
        mime_type: str = "image/jpeg",
    ) -> dict[str, Any]:

        if not self.client:
            raise RuntimeError(
                "Gemini is not configured."
            )

        contents: list[Any] = [
            SYSTEM_PROMPT
            + "\n\n"
            + prompt
        ]

        if image_bytes:
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
            )

        response = (
            self.client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
            )
        )

        text = response.text or ""

        return self._parse_json(text)

    @staticmethod
    def _parse_json(
        text: str,
    ) -> dict[str, Any]:

        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines:
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip()
                == "```"
            ):
                lines = lines[:-1]

            text = "\n".join(
                lines
            ).strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON."
            ) from exc


gemini_service = GeminiService()