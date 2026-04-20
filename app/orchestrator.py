import time
from app.market import IndianMarketMCP
from app.calculators import (
    calculate_sip_growth,
    calculate_ppf_growth,
    calculate_fd_growth,
    calculate_credit_card_payoff_india,
)
from app.observability import ProductionLogger
from app.agents import build_profiler, build_advisor, parse_profile


logger = ProductionLogger()
market = IndianMarketMCP()
profiler = build_profiler()
advisor = build_advisor()


async def run_finpath_india(user_query: str) -> dict:
    start = time.time()
    trace_id = logger.start_trace(user_query)

    try:
        profile_raw = profiler.send_message(user_query)
        logger.log_agent_event(trace_id, "IndianProfiler", profile_raw)
        profile = parse_profile(profile_raw)

        nifty = market.get_nifty_return(1)
        ppf = market.get_ppf_rate()
        fd = market.get_fd_rates()

        logger.log_tool_call(trace_id, "get_nifty_return", nifty)
        logger.log_tool_call(trace_id, "get_ppf_rate", ppf)
        logger.log_tool_call(trace_id, "get_fd_rates", fd)

        has_debt = profile.debt_amount > 0

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

        advisor_prompt = f"""
Original user query:
{user_query}

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
"""

        recommendation = advisor.send_message(advisor_prompt)
        logger.log_agent_event(trace_id, "IndianFinancialAdvisor", recommendation)

        duration_ms = (time.time() - start) * 1000
        logger.complete_trace(trace_id, duration_ms, success=True)

        return {
            "recommendation": recommendation,
            "profile": profile.model_dump(),
            "market_data": {"nifty": nifty, "ppf": ppf, "fd": fd},
            "quant_analysis": quant_analysis,
            "trace_id": trace_id,
            "currency": "INR",
            "has_debt": has_debt,
        }

    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.complete_trace(trace_id, duration_ms, success=False)
        return {
            "error": str(e),
            "trace_id": trace_id,
        }