import bankroll_simulator as sim


def test_run_once_uses_dummy_simulation(monkeypatch):
    """_run_once should return 'ran_out' with zero winnings when simulation does nothing."""

    def fake_simulate(self, **kwargs):
        return None

    monkeypatch.setattr(sim.Blackjack, "simulate", fake_simulate)

    outcome, winnings, hands_played = sim._run_once(
        seed=1, number_of_shoes=1, penetration=0.5, shoe_size=1
    )

    assert outcome == "ran_out"
    assert winnings == 0
    assert hands_played == 0
