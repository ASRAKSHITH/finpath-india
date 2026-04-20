def calculate_sip_growth(monthly_investment: float, annual_return: float, years: int, existing_investment: float = 0) -> dict:
    years = int(years)
    monthly_rate = annual_return / 12
    months = years * 12

    if monthly_rate == 0:
        sip_value = monthly_investment * months
    else:
        sip_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    existing_grown = existing_investment * ((1 + annual_return) ** years)
    total_value = sip_value + existing_grown
    total_invested = existing_investment + (monthly_investment * months)
    gains = total_value - total_invested

    return {
        "scenario": "SIP Investment",
        "future_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "gains": round(gains, 2),
        "currency": "INR",
    }


def calculate_ppf_growth(annual_deposit: float, years: int, ppf_rate: float, existing_balance: float = 0) -> dict:
    years = int(years)

    if annual_deposit > 150000:
        annual_deposit = 150000

    balance = existing_balance
    for _ in range(years):
        balance = (balance + annual_deposit) * (1 + ppf_rate)

    total_invested = existing_balance + (annual_deposit * years)
    gains = balance - total_invested

    return {
        "scenario": "PPF Investment",
        "maturity_value": round(balance, 2),
        "total_invested": round(total_invested, 2),
        "gains": round(gains, 2),
        "currency": "INR",
    }


def calculate_fd_growth(principal: float, fd_rate: float, years: int) -> dict:
    years = int(years)
    maturity = principal * ((1 + fd_rate / 4) ** (years * 4))

    return {
        "scenario": "Fixed Deposit",
        "maturity_value": round(maturity, 2),
        "principal": round(principal, 2),
        "total_interest": round(maturity - principal, 2),
        "currency": "INR",
    }


def calculate_credit_card_payoff_india(principal: float, monthly_payment: float, apr: float) -> dict:
    monthly_rate = apr / 12
    balance = float(principal)
    total_interest = 0
    months = 0

    if monthly_payment <= balance * monthly_rate:
        return {
            "error": "Monthly payment too low to cover interest."
        }

    while balance > 0 and months < 360:
        interest = balance * monthly_rate
        total_interest += interest
        principal_payment = min(monthly_payment - interest, balance)
        balance -= principal_payment
        months += 1

    return {
        "scenario": "Pay Credit Card Debt",
        "total_interest_paid": round(total_interest, 2),
        "total_paid": round(principal + total_interest, 2),
        "months_to_clear": months,
        "years_to_clear": round(months / 12, 1),
        "currency": "INR",
    }