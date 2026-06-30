import time
from pydantic import ValidationError
from app.market import IndianMarketMCP
from app.calculators import (
    calculate_sip_growth,
    calculate_ppf_growth,
    calculate_fd_growth,
    calculate_credit_card_payoff_india,
)
from app.observability import ProductionLogger
from app.agents import build_profiler, build_advisor, build_archivist, parse_profile, run_agent

logger = ProductionLogger()
market = IndianMarketMCP()
profiler = build_profiler()
advisor = build_advisor()
archivist = build_archivist()

# Circuit Breaker: Prevent infinite loops / DoW attacks
MAX_EXECUTION_STEPS = 10

async def run_finpath_india(user_query: str, history: list = None) -> dict:
    if history is None:
        history = []
        
    start = time.time()
    trace_id = logger.start_trace(user_query)
    steps_taken = 0

    try:
        # Context Engineering: Rolling Summary (Memory)
        rolling_summary = ""
        if history:
            steps_taken += 1
            history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in history])
            archivist_prompt = f"Conversation History:\n{history_text}\n\nLatest Query: {user_query}"
            rolling_summary = run_agent(archivist, archivist_prompt)
            logger.log_agent_event(trace_id, "IndianArchivist", rolling_summary)
            
        steps_taken += 1
        profiler_prompt = user_query
        if rolling_summary:
            profiler_prompt = f"Previous context: {rolling_summary}\n\nUpdate profile based on new info: {user_query}"
            
        profile_raw = run_agent(profiler, profiler_prompt)
        logger.log_agent_event(trace_id, "IndianProfiler", profile_raw)

        try:
            profile = parse_profile(profile_raw)
        except (ValueError, ValidationError) as exc:
            raise ValueError(f"Profile extraction failed: {exc}") from exc

        if profile.time_horizon < 1:
            raise ValueError("time_horizon must be at least 1 year.")
        if profile.monthly_surplus < 0:
            raise ValueError("monthly_surplus cannot be negative.")
        if profile.debt_amount < 0:
            raise ValueError("debt_amount cannot be negative.")

        steps_taken += 1
        nifty = market.get_nifty_return(1)
        ppf = market.get_ppf_rate()
        fd = market.get_fd_rates()

        logger.log_tool_call(trace_id, "get_nifty_return", nifty)
        logger.log_tool_call(trace_id, "get_ppf_rate", ppf)
        logger.log_tool_call(trace_id, "get_fd_rates", fd)

        has_debt = profile.debt_amount > 0

        steps_taken += 1
        sip_result = calculate_sip_growth(
            monthly_investment=profile.monthly_surplus,
            annual_return=nifty["annual_return"] or 0.10,
            years=profile.time_horizon,
            existing_investment=profile.savings_amount,
        )

        ppf_result = calculate_ppf_growth(
            annual_deposit=min(profile.monthly_surplus * 12, 150000),
            years=profile.time_horizon,
            ppf_rate=ppf["annual_return"],
            existing_balance=profile.savings_amount,
        )

        fd_result = calculate_fd_growth(
            principal=profile.savings_amount,
            fd_rate=fd["annual_return"],
            years=profile.time_horizon,
        )

        debt_result = None
        if has_debt:
            debt_result = calculate_credit_card_payoff_india(
                principal=profile.debt_amount,
                monthly_payment=profile.monthly_surplus,
                apr=profile.debt_interest_rate,
            )

        quant_analysis = {
            "sip": sip_result,
            "ppf": ppf_result,
            "fd": fd_result,
            "debt": debt_result,
        }

        # Safely handle None values from market APIs (e.g., if Yahoo Finance blocks the cloud IP)
        nifty_rate = (nifty['annual_return'] or 0.10) * 100
        ppf_rate = (ppf['annual_return'] or 0.071) * 100
        fd_rate = (fd['annual_return'] or 0.068) * 100

        # Vibe Diff (Plain-English Execution Summary)
        vibe_diff = (
            f"Execution Plan (Vibe Diff):\n"
            f"- Interpreted Profile: {profile.time_horizon} years horizon, ₹{profile.monthly_surplus} monthly surplus, ₹{profile.debt_amount} debt.\n"
            f"- Market Data Retrieved: Nifty 50 ({nifty_rate:.1f}%), PPF ({ppf_rate:.1f}%), FD ({fd_rate:.1f}%).\n"
            f"- Calculators Run: SIP, PPF, FD" + (", Credit Card Payoff" if has_debt else "") + ".\n"
            f"- Next Action: Passing all quantitative insights to IndianFinancialAdvisor for final synthesis."
        )
        logger.log_agent_event(trace_id, "VibeDiff", vibe_diff)

        advisor_prompt = f"""
Original user query:
{user_query}

{"Previous Context (Rolling Summary):\n" + rolling_summary + "\n" if rolling_summary else ""}
Profile:
{profile.model_dump()}

Market data:
{{
  "nifty": {nifty},
  "ppf": {ppf},
  "fd": {fd}
}}

Quantitative analysis:
{quant_analysis}

Please produce:
1. Recommendation
2. The Numbers
3. Counterfactual
4. Tax Impact
5. Data Transparency

If the user's query is in English, answer in English. If the user's query is in Hindi, answer in Hindi.
"""

        steps_taken += 1
        if steps_taken > MAX_EXECUTION_STEPS:
            raise RuntimeError("Circuit Breaker Triggered: Maximum execution steps exceeded.")
            
        recommendation = run_agent(advisor, advisor_prompt)
        logger.log_agent_event(trace_id, "IndianFinancialAdvisor", recommendation)

        duration_ms = (time.time() - start) * 1000
        logger.complete_trace(trace_id, duration_ms, success=True)

        return {
            "recommendation": recommendation,
            "profile": profile.model_dump(),
            "market_data": {"nifty": nifty, "ppf": ppf, "fd": fd},
            "quant_analysis": quant_analysis,
            "vibe_diff": vibe_diff,
            "trace_id": trace_id,
            "currency": "INR",
            "has_debt": has_debt,
        }

    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.log_agent_event(trace_id, "Error", str(e))
        logger.complete_trace(trace_id, duration_ms, success=False)
        return {
            "error": str(e),
            "trace_id": trace_id,
        }