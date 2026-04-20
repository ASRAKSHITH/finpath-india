import json
import google.generativeai as genai
from app.schemas import UserProfile


class FinPathAgent:
    def __init__(self, name: str, system_instruction: str, model_name: str = "gemini-2.5-flash"):
        self.name = name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        self.chat = self.model.start_chat()

    def send_message(self, message: str) -> str:
        response = self.chat.send_message(message)
        return response.text


def build_profiler():
    return FinPathAgent(
        name="IndianProfiler",
        model_name="gemini-2.5-flash",
        system_instruction="""
You extract financial profile data from Indian users.
Return ONLY valid JSON with:
savings_amount, debt_amount, debt_interest_rate, monthly_surplus, time_horizon, investment_preference
Use 0 where value is missing.
time_horizon must be an integer.
"""
    )


def parse_profile(text: str) -> UserProfile:
    clean = text.strip()
    if "{" in clean and "}" in clean:
        clean = clean[clean.index("{"):clean.rindex("}") + 1]

    data = json.loads(clean)
    return UserProfile(**data)


def build_advisor():
    return FinPathAgent(
        name="IndianFinancialAdvisor",
        model_name="gemini-2.5-flash",
        system_instruction="""
You are a financial decision assistant for Indian users.
Give clear, actionable advice in the same language as the user's query.
Explain recommendation, numbers, counterfactual, tax impact, and data transparency.
"""
    )