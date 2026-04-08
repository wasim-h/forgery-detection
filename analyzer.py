import google.generativeai as genai
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

ANALYSIS_PROMPT = """You are a forensic document analyst specializing in ID document forgery detection.
Analyze this ID document image for signs of forgery or tampering.

Check for:
1. Font inconsistencies (mixed fonts, unusual spacing, misaligned text)
2. Image quality anomalies (blurring, pixelation around text/photo)
3. Color inconsistencies (uneven background, color bleeding)
4. Photo tampering (edges around photo, mismatched lighting)
5. Security features (holograms, watermarks, microprint if visible)
6. Layout issues (misaligned fields, incorrect proportions)
7. Text anomalies (unusual characters, incorrect date formats)

Respond ONLY with this JSON structure, no extra text, no markdown backticks:
{
  "verdict": "GENUINE" or "SUSPICIOUS" or "LIKELY_FORGED",
  "risk_score": <integer 0-100, where 0=definitely genuine, 100=definitely forged>,
  "summary": "<one sentence overall assessment>",
  "findings": [
    {
      "category": "<category name>",
      "status": "OK" or "WARNING" or "ALERT",
      "detail": "<specific observation>"
    }
  ],
  "red_flags": ["<list of specific suspicious elements, empty if none>"],
  "recommendation": "<what action should be taken>"
}"""

def analyze_document(image_bytes: bytes, media_type: str) -> dict:
    image_part = {
        "mime_type": media_type,
        "data": base64.b64encode(image_bytes).decode("utf-8")
    }

    response = model.generate_content([
        ANALYSIS_PROMPT,
        {"inline_data": image_part}
    ])

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)