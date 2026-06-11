import json
import google.generativeai as genai
from app.schemas import UserProfile


class FinPathAgent:
    def __init__(self, name: str, system_instruction: str, model_name: str = "gemini-2.5-flash-lite"):
        self.name = name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )

    def send_message(self, message: str) -> str:
        chat = self.model.start_chat()
        response = chat.send_message(message)
        return response.text


def build_profiler():
    return FinPathAgent(
        name="IndianProfiler",
        model_name="gemini-2.5-flash-lite",
        system_instruction="""
You extract financial profile data from Indian users.
Return ONLY valid JSON with:
savings_amount, debt_amount, debt_interest_rate, monthly_surplus, time_horizon, investment_preference
Use 0 where numeric value is missing.
For investment_preference, use "market" if missing.
time_horizon must be an integer.
If the user's query is in English, respond in English. If the user's query is in Hindi, respond in Hindi.
"""
    )


def parse_profile(text: str) -> UserProfile:
    clean = text.strip()
    if "{" in clean and "}" in clean:
        clean = clean[clean.index("{"):clean.rindex("}") + 1]
    else:
        raise ValueError("Profiler output did not contain a JSON object.")

    try:
        data = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Unable to parse profile JSON from agent output: {exc.msg}") from exc

    return UserProfile(**data)


def build_advisor():
    return FinPathAgent(
        name="IndianFinancialAdvisor",
        model_name="gemini-2.5-flash-lite",
        system_instruction="""
You are a financial decision assistant for Indian users.
Give clear, actionable advice in the same language as the user's query.
If the user's query is in English, respond in English. If the user's query is in Hindi, respond in Hindi.
Explain recommendation, numbers, counterfactual, tax impact, and data transparency.
"""
    )