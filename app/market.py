from datetime import datetime
import yfinance as yf


class IndianMarketMCP:
    def __init__(self):
        self.rate_cache = {}
        self.cache_timestamp = {}

    def get_nifty_return(self, period_years: int = 1) -> dict:
        try:
            period_str = f"{int(period_years)}y"
            nifty = yf.Ticker("^NSEI")
            hist = nifty.history(period=period_str)

            if len(hist) < 2:
                raise ValueError("Insufficient historical data")

            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            annual_return = (end_price / start_price) - 1

            return {
                "annual_return": round(float(annual_return), 4),
                "index": "Nifty 50",
                "current_value": round(float(end_price), 2),
                "data_source": "YahooFinance NSE",
                "timestamp": datetime.now().isoformat(),
                "data_points": len(hist),
            }
        except Exception as e:
            return {
                "error": str(e),
                "annual_return": None,
                "index": "Nifty 50",
                "data_source": "FAILED",
                "timestamp": datetime.now().isoformat(),
            }

    def get_ppf_rate(self, force_refresh: bool = False) -> dict:
        return {
            "annual_return": 0.071,
            "scheme": "PPF",
            "effective_from": "Oct 2025",
            "features": "Tax-free EEE, 15-year lock-in, Govt-backed",
            "max_deposit_annual": 150000,
            "data_source": "GOI Quarterly Update",
            "timestamp": datetime.now().isoformat(),
            "note": "Replace with live government source fetch later.",
        }

    def get_fd_rates(self, bank: str = "average") -> dict:
        fd_rates_db = {
            "sbi": 0.0700,
            "hdfc": 0.0700,
            "icici": 0.0675,
            "average": 0.0685,
        }
        rate = fd_rates_db.get(bank.lower(), fd_rates_db["average"])

        return {
            "annual_return": rate,
            "scheme": f"Fixed Deposit - {bank.upper()}",
            "tenure": "1 year",
            "features": "Guaranteed returns",
            "data_source": f"{bank.upper()} website / reference",
            "timestamp": datetime.now().isoformat(),
        }