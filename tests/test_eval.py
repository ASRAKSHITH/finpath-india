import pytest
from google import genai
from app.orchestrator import run_finpath_india

# Mock Kaggle Evaluation setup using LLM-as-judge for Intent Satisfaction
client = genai.Client()

@pytest.mark.asyncio
async def test_intent_satisfaction():
    user_query = "I have ₹50,000 to invest monthly for 5 years. I have ₹2,00,000 in credit card debt. Should I invest or pay debt?"
    
    # 1. Run the system
    response = await run_finpath_india(user_query)
    
    # Ensure it ran successfully
    assert "error" not in response
    assert response["has_debt"] is True

    recommendation = response["recommendation"]
    vibe_diff = response["vibe_diff"]
    
    # 2. Derive evaluation criteria using LLM as Judge (Agent-as-a-Judge / Process Evaluation)
    eval_prompt = f"""
    You are an expert AI Agent judge.
    Evaluate the internal thought process and execution trace of the following financial agent.
    
    User Query: {user_query}
    
    Internal Profiler Output:
    {response.get('profile', {})}
    
    Internal Market Data Used:
    {response.get('market_data', {})}
    
    Agent Execution Plan (Vibe Diff):
    {vibe_diff}
    
    Agent Final Recommendation:
    {recommendation}
    
    Process Evaluation Questions:
    1. Did the Profiler correctly extract the 2,00,000 debt amount into the internal profile JSON?
    2. Did the Execution Plan (Vibe Diff) correctly state the tools it ran?
    3. Did the final recommendation explicitly advise paying off the 2 Lakh credit card debt before heavy investing based on the parsed data?
    
    Did the agent pass all process checks? (Yes/No).
    Output exactly 'Yes' or 'No'.
    """
    
    judgment = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=eval_prompt
    ).text.strip()
    
    assert "Yes" in judgment, f"Process evaluation failed. Judge response: {judgment}"
