from fastapi.testclient import TestClient
from app.main import app
from app import orchestrator


def test_analyze_endpoint_returns_result(monkeypatch):
    dummy_response = {
        "recommendation": "Test recommendation",
        "profile": {
            "savings_amount": 100000,
            "debt_amount": 0,
            "debt_interest_rate": 0,
            "monthly_surplus": 20000,
            "time_horizon": 5,
            "investment_preference": "market",
        },
        "market_data": {
            "nifty": {"annual_return": 0.1},
            "ppf": {"annual_return": 0.071},
            "fd": {"annual_return": 0.0685},
        },
        "quant_analysis": {"sip": {}, "ppf": {}, "fd": {}, "debt": None},
        "trace_id": "trace0001",
        "currency": "INR",
        "has_debt": False,
    }

    monkeypatch.setattr(orchestrator, "run_finpath_india", lambda query: dummy_response)
    client = TestClient(app)

    response = client.post("/analyze", json={"query": "I have 1 lakh savings and no debt."})

    assert response.status_code == 200
    assert response.json() == dummy_response


def test_parse_profile_extracts_json_from_text():
    from app.agents import parse_profile

    raw_text = "Here is the extracted profile: {\n  \"savings_amount\": 50000,\n  \"debt_amount\": 10000,\n  \"debt_interest_rate\": 0.24,\n  \"monthly_surplus\": 15000,\n  \"time_horizon\": 8,\n  \"investment_preference\": \"market\"\n}"
    profile = parse_profile(raw_text)

    assert profile.savings_amount == 50000
    assert profile.debt_amount == 10000
    assert profile.time_horizon == 8
    assert profile.investment_preference == "market"
