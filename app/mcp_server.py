from mcp.server.fastmcp import FastMCP
from app.market import IndianMarketMCP
from app.calculators import (
    calculate_sip_growth,
    calculate_ppf_growth,
    calculate_fd_growth,
    calculate_credit_card_payoff_india,
)

mcp = FastMCP("finpath-market-tools")
market = IndianMarketMCP()

@mcp.tool()
def get_nifty_return(period_years: int = 1) -> dict:
    """Fetch live Nifty 50 return for given period in years."""
    return market.get_nifty_return(period_years)

@mcp.tool()
def get_ppf_rate(force_refresh: bool = False) -> dict:
    """Fetch current Indian Public Provident Fund (PPF) interest rate."""
    return market.get_ppf_rate(force_refresh)

@mcp.tool()
def get_fd_rates(bank: str = "average") -> dict:
    """Fetch current Indian Fixed Deposit (FD) interest rates for a bank (sbi, hdfc, icici, average)."""
    return market.get_fd_rates(bank)

@mcp.tool()
def calc_sip(monthly_investment: float, annual_return: float, years: int, existing_investment: float = 0.0) -> dict:
    """Calculate future value of a Systematic Investment Plan (SIP)."""
    return calculate_sip_growth(monthly_investment, annual_return, years, existing_investment)

@mcp.tool()
def calc_ppf(annual_deposit: float, years: int, ppf_rate: float = 0.071, existing_balance: float = 0.0) -> dict:
    """Calculate future value of Indian PPF investment."""
    return calculate_ppf_growth(annual_deposit, years, ppf_rate, existing_balance)

@mcp.tool()
def calc_fd(principal: float, fd_rate: float, years: int) -> dict:
    """Calculate future value of Indian Fixed Deposit."""
    return calculate_fd_growth(principal, fd_rate, years)

@mcp.tool()
def calc_credit_card_payoff(principal: float, monthly_payment: float, apr: float) -> dict:
    """Calculate time to payoff Indian credit card debt."""
    return calculate_credit_card_payoff_india(principal, monthly_payment, apr)

if __name__ == "__main__":
    # To run this MCP server over standard input/output (stdio)
    mcp.run()
