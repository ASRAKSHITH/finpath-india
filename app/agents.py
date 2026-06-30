import json
from google.adk.agents import LlmAgent
from google import genai
from google.genai import types
from app.schemas import UserProfile

client = genai.Client()

import time

def run_agent(agent: LlmAgent, prompt: str) -> str:
    max_retries = 4
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=agent.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=agent.instruction
                )
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            
            # Catch transient errors: 503 (Unavailable) or 429 (Too Many Requests)
            if "503" in error_str or "429" in error_str:
                if attempt == max_retries - 1:
                    # If we exhausted retries and it's a 429, give a friendly message
                    if "429" in error_str:
                        raise ValueError("Our free AI tier is currently resting due to high traffic. Please wait 30 to 60 seconds and try your request again!")
                    raise e
                
                sleep_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"API throttled (503/429). Retrying in {sleep_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(sleep_time)
            else:
                if attempt == max_retries - 1:
                    raise e

def build_profiler():
    return LlmAgent(
        name="IndianProfiler",
        model="gemini-2.5-flash",
        instruction="""
You extract financial profile data from Indian users.
Return ONLY valid JSON with:
savings_amount, debt_amount, debt_interest_rate, monthly_surplus, time_horizon, investment_preference
Use 0 where numeric value is missing.
For investment_preference, use "market" if missing.
time_horizon must be an integer.
time_horizon must be an integer.
CRITICAL RULE: You MUST respond in the EXACT same language as the user's prompt. If the prompt is purely English, your response MUST be 100% English. If you detect English, do not use Hindi.
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
    return LlmAgent(
        name="IndianFinancialAdvisor",
        model="gemini-2.5-flash",
        instruction="""
You are a financial decision assistant for Indian users.
CRITICAL RULE: You MUST respond in the EXACT same language as the user's prompt. If the prompt is purely English, your response MUST be 100% English. If you detect English, do not use Hindi.
Explain recommendation, numbers, counterfactual, tax impact, and data transparency.
"""
    )

def build_archivist():
    return LlmAgent(
        name="IndianArchivist",
        model="gemini-2.5-flash",
        instruction="""
You are a memory archivist for a financial agent. 
Read the provided conversation history and extract a concise, updated "Rolling Summary" of the user's financial profile, goals, and constraints. 
Only output the factual summary. Ignore pleasantries.
"""
    )