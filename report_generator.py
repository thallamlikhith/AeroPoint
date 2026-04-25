"""
report_generator.py
Generates multilingual, role-based badminton reports using Gemini 2.5 Flash.
Fully compatible with google-generativeai >= 0.6 (v0.8.5 supported).
Includes safe fallback when API fails.
"""

import json
import textwrap
import logging
from typing import List, Dict, Literal
import google.generativeai as genai

logger = logging.getLogger(__name__)

ReportRole = Literal["coach", "student", "parent"]


# --------------------------------------------
# Initialize Gemini (2.5 Flash)
# --------------------------------------------
def init_gemini(api_key: str):
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini API initialized successfully.")
    except Exception as e:
        logger.error(f"Gemini configuration error: {e}")


# --------------------------------------------
# Role prompts
# --------------------------------------------
def _role_prompt(role: ReportRole, player_num: int, locale: str):
    player_ref = f"Player {player_num}"

    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
        "ta": "Tamil",
        "kn": "Kannada"
    }
    language = lang_map.get(locale, "English")

    prompts = {
        "coach": f"You are an elite badminton coach analyzing {player_ref}. Provide deep, technical, timestamped feedback in {language}.",
        "student": f"You are a friendly coach teaching {player_ref}. Give simple, clear instructions in {language}.",
        "parent": f"Explain {player_ref}'s progress to a parent using non-technical language in {language}."
    }

    return textwrap.dedent(prompts.get(role, prompts["coach"]))


def _structure(role: ReportRole):
    structures = {
        "coach": "1. Technical Mechanics\n2. Tactical Choices\n3. Physical Metrics\n4. Mistakes\n5. Drills",
        "student": "1. Strengths\n2. Improvement Areas\n3. Drills\n4. Weekly Plan",
        "parent": "1. Summary\n2. Strengths\n3. Support Areas\n4. Next Steps"
    }
    return structures.get(role, structures["coach"])


# --------------------------------------------
# Main Report Generator using Gemini 2.5 Flash
# --------------------------------------------
def generate_report(
    pose_metrics: List[Dict],
    mistakes: List[Dict],
    transcription: str,
    role: ReportRole,
    player_num: int,
    locale: str
) -> str:

    role_prompt = _role_prompt(role, player_num, locale)
    structure = _structure(role)

    # Reduced data snippet for safety
    snippet = json.dumps({
        "frames_processed": len(pose_metrics),
        "mistakes": mistakes[:8]
    }, indent=2)

    prompt = f"""
{role_prompt}

Use this structure:
{structure}

Guidelines:
- Add timestamps where helpful
- Use bullet points
- Keep tone appropriate for the role
- Reply ONLY in the target language
- Make feedback actionable

Key Data:
{snippet}
"""

    # ------------------------------
    # Gemini 2.5 Flash API call
    # ------------------------------
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text.strip()

        raise RuntimeError("Empty Gemini response received.")

    except Exception as e:
        logger.warning(f"⚠ Gemini failure → Fallback activated. Reason: {e}")
        return _fallback_report(pose_metrics, mistakes, role, player_num, locale)


# --------------------------------------------
# Fallback Report (Offline Mode)
# --------------------------------------------
def _fallback_report(pose_metrics, mistakes, role, player_num, locale):
    lines = []
    lines.append("BADMINTON REPORT (OFFLINE MODE)")
    lines.append(f"Role: {role}")
    lines.append(f"Player: {player_num}")
    lines.append(f"Language: {locale}")
    lines.append("")
    lines.append(f"Frames analyzed: {len(pose_metrics)}")
    lines.append(f"Mistakes detected: {len(mistakes)}")
    lines.append("")

    if mistakes:
        lines.append("Sample mistakes:")
        for m in mistakes[:5]:
            lines.append(f"- Time {m['time']:.2f}s → {m.get('mistake_types')}")

    lines.append("\nGeneral Improvement Tips:")
    lines.append("- Improve reaction stance.")
    lines.append("- Increase wrist acceleration.")
    lines.append("- Work on knee-bend depth.")
    lines.append("- Strengthen footwork consistency.")

    return "\n".join(lines)
