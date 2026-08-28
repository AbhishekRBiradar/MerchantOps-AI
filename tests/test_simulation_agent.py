from backend.agents.simulation_agent import SimulationAgent


def test_simulation_generates_three_scenarios():

    agent = SimulationAgent()

    candidates = [
        {
            "payment_id": "PAY001",
            "amount": 1000,
            "risk_score": 0.20,
            "risk_level": "LOW",
            "retry_count": 0,
        }
    ]

    result = agent.simulate(
        candidates
    )

    assert len(result) == 1

    scenarios = result[0][
        "simulation_scenarios"
    ]

    assert len(scenarios) == 3

    actions = {
        scenario["action"]
        for scenario in scenarios
    }

    assert actions == {
        "RETRY_NOW",
        "RETRY_LATER",
        "DO_NOTHING",
    }


def test_high_risk_does_not_auto_retry():

    agent = SimulationAgent()

    candidates = [
        {
            "payment_id": "PAY002",
            "amount": 5000,
            "risk_score": 0.80,
            "risk_level": "HIGH",
            "retry_count": 3,
        }
    ]

    result = agent.simulate(
        candidates
    )

    assert len(result) == 1

    assert (
        result[0]["recommended_action"]
        == "DO_NOTHING"
    )