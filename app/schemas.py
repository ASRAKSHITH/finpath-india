from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    savings_amount: float = Field(default=0)
    debt_amount: float = Field(default=0)
    debt_interest_rate: float = Field(default=0)
    monthly_surplus: float = Field(default=0)
    time_horizon: int = Field(default=1)
    investment_preference: str = Field(default="market")

    @field_validator("investment_preference", mode="before")
    @classmethod
    def fix_investment_preference(cls, v):
        if v in [None, "", 0, "0"]:
            return "market"
        return str(v)


class FinPathRequest(BaseModel):
    query: str


class FinPathResponse(BaseModel):
    recommendation: str
    profile: dict
    market_data: dict
    quant_analysis: dict | str
    trace_id: str
    currency: str = "INR"
    has_debt: bool