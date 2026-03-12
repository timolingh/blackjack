import concurrent.futures
import multiprocessing as mp
import os
import numpy as np
from blackjack.blackjack import Blackjack
from blackjack.card_counter import CardCounter
from blackjack.enums import CardCountingSystem


def _fmt_money(amount: float) -> str:
    """Format a numeric amount as USD-style string."""
    return f"${amount:,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"


def _make_blackjack():
    return Blackjack(
        min_bet=15,
        max_bet=2000,
        s17=False,
        blackjack_payout=1.5,
        max_hands=4,
        double_down=True,
        double_after_split=True,
        resplit_aces=False,
        insurance=True,
        late_surrender=False,
        dealer_shows_hole_card=True
    )


def _make_player():
    return CardCounter(
        name='CC_1',
        bankroll=20000,
        min_bet=15,
        card_counting_system=CardCountingSystem.HI_LO,
        stop_on_goal=True,
        bankroll_goal=40000,
        bet_ramp={
            0: 15,
            1: 30,
            2: 50,
            3: 75,
            4: 100,
            5: 125  
        },
        insurance=3
    )


def _run_once(seed: int, number_of_shoes: int, penetration: float, shoe_size: int):
    """
    Execute one simulation run and return (outcome, winnings, hands_played).
    Outcome is one of {'bankrupt', 'goal', 'ran_out'}.
    """
    # Diagnostic: show which process is running which seed.
    # Remove or comment out if noisy.
    print(f"Seed {seed} running on PID {os.getpid()}")

    blackjack = _make_blackjack()
    player = _make_player()
    initial_bankroll = player.bankroll
    blackjack.add_player(player=player)
    blackjack.simulate(
        penetration=penetration,
        number_of_shoes=number_of_shoes,
        shoe_size=shoe_size,
        seed=seed,
        reset_bankroll=False,
        progress_bar=False,
        _logfile=None
    )
    stats_dict = player.stats.summary(string=False)
    hands_played = stats_dict.get('TOTAL HANDS PLAYED', 0)
    winnings = player.bankroll - initial_bankroll
    if player.is_ruined:
        outcome = 'bankrupt'
    elif player.bankroll_goal_reached:
        outcome = 'goal'
    else:
        outcome = 'ran_out'
    return outcome, winnings, hands_played


def main():
    """
    Run simulate multiple times and report counts of bankrupt/goal/ran-out,
    average winnings, and total hands played across runs.
    """

    number_of_runs = 10    
    number_of_shoes = 2000 
    penetration = 4.0 / 6.0
    shoe_size = 6

    bankrupt_count = 0
    goal_count = 0
    ran_out_count = 0
    total_winnings_accum = 0
    total_hands_accum = 0
    winnings_samples: list[float] = []

    max_workers = min(number_of_runs, os.cpu_count() or 2)

    try:
        executor_cls = concurrent.futures.ProcessPoolExecutor
        executor_kwargs = {"max_workers": max_workers, "mp_context": mp.get_context("fork")}
        with executor_cls(**executor_kwargs) as executor:
            futures = [
                executor.submit(_run_once, seed=run_idx, number_of_shoes=number_of_shoes, penetration=penetration, shoe_size=shoe_size)
                for run_idx in range(number_of_runs)
            ]
            for future in concurrent.futures.as_completed(futures):
                outcome, winnings, hands_played = future.result()
                if outcome == 'bankrupt':
                    bankrupt_count += 1
                elif outcome == 'goal':
                    goal_count += 1
                else:
                    ran_out_count += 1
                total_winnings_accum += winnings
                total_hands_accum += hands_played
                winnings_samples.append(winnings)
    except PermissionError:
        # Some environments forbid process pools; fall back to threads.
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(_run_once, seed=run_idx, number_of_shoes=number_of_shoes, penetration=penetration, shoe_size=shoe_size)
                for run_idx in range(number_of_runs)
            ]
            for future in concurrent.futures.as_completed(futures):
                outcome, winnings, hands_played = future.result()
                if outcome == 'bankrupt':
                    bankrupt_count += 1
                elif outcome == 'goal':
                    goal_count += 1
                else:
                    ran_out_count += 1
                total_winnings_accum += winnings
                total_hands_accum += hands_played
                winnings_samples.append(winnings)

    avg_total_winnings = total_winnings_accum / number_of_runs
    risk_of_ruin = bankrupt_count / number_of_runs
    if winnings_samples:
        p20, p80 = np.percentile(winnings_samples, [20, 80])
    else:
        p20 = p80 = 0.0

    print("Simulation results")
    print(f"Runs: {number_of_runs}")
    print(f"Shoes per run: {number_of_shoes}")
    print(f"Bankrupt count: {bankrupt_count}")
    print(f"Bankroll goal count: {goal_count}")
    print(f"Ran out of shoes: {ran_out_count}")
    print(f"Average total winnings: {_fmt_money(avg_total_winnings)}")
    print(f"20th percentile winnings: {_fmt_money(p20)}")
    print(f"80th percentile winnings: {_fmt_money(p80)}")
    print(f"Total hands played across runs: {total_hands_accum}")
    print(f"Risk of ruin: {risk_of_ruin:.2%}")

    return 0


if __name__ == "__main__":
    main()
