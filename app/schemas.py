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


class Message(BaseModel):
    role: str
    content: str

class FinPathRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=500, description="User financial query. Limited to 500 characters to prevent prompt injection.")
    history: list[Message] = Field(default=[], description="Previous conversation history")

class FinPathFeedback(BaseModel):
    trace_id: str
    feedback: str


class FinPathResponse(BaseModel):
    recommendation: str
    profile: dict
    market_data: dict
    quant_analysis: dict | str
    trace_id: str
    currency: str = "INR"
    has_debt: bool