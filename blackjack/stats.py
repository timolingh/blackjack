from collections import defaultdict
from blackjack.enums import StatsCategory

# class Variance:
#     """
#     """
#     def __init__(self, bankroll):
#         self.bankroll = bankroll
#         self.count = 0
#         self.earnings_mean = 0
#         self.m2 = 0
#         self.earnings_variance = float("nan")

#     def update_aggregate(self, bankroll):
#         self.count += 1
#         earnings = bankroll - self.bankroll
#         delta = earnings - self.earnings_mean
#         updated_mean = self.earnings_mean + (delta / self.count)
#         delta2 = earnings - updated_mean
#         self.m2 += delta * delta2

#         self.bankroll = bankroll
#         self.earnings_mean = updated_mean
#         if self.count >= 2:
#             self.earnings_variance = self.m2 / self.count

class Variance:
    """
    Track running mean and variance of earnings relative to an initial bankroll.
    """

    def __init__(self, bankroll):
        """
        Initialize a Variance tracker for a bankroll process.

        Args:
            bankroll (float): Initial bankroll used as the baseline for earnings.
        """
        self.bankroll = bankroll
        self.count = 0
        self.earnings_mean = 0
        self.m2 = 0
        self.earnings_variance = float("nan")

    def update_aggregate(self, bankroll):
        """
        Update running earnings mean and variance given a new bankroll value.

        This uses Welford's online algorithm to update the second central moment.
        https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance

        Args:
            bankroll (float): New bankroll after the latest trial or hand.

        Side effects:
            Updates:
            - self.count: Number of updates processed.
            - self.bankroll: Last observed bankroll.
            - self.earnings_mean: Running mean of earnings.
            - self.m2: Accumulated second central moment.
            - self.earnings_variance: Current variance estimate (population form when count >= 2).
        """
        self.count += 1
        earnings = bankroll - self.bankroll
        delta = earnings - self.earnings_mean
        updated_mean = self.earnings_mean + (delta / self.count)
        delta2 = earnings - updated_mean
        self.m2 += delta * delta2

        self.bankroll = bankroll
        self.earnings_mean = updated_mean
        if self.count >= 2:
            self.earnings_variance = self.m2 / self.count


class Stats:
    """
    Represents a way to store blackjack statistics
    over the course of a simulation.

    """
    def __init__(self):
        self._stats = defaultdict(float)

    @property
    def stats(self) -> defaultdict[tuple[float | int | None, StatsCategory], float]:
        return self._stats

    def _compute_totals(self) -> defaultdict[str, float]:
        totals: defaultdict[str, float] = defaultdict(float)
        for stats_key, value in self._stats.items():
            totals[stats_key[1].value] += value
        return totals

    def _get_total(self, totals: defaultdict[str, float], *categories: StatsCategory) -> float:
        return sum(totals.get(category.value, 0) for category in categories)

    def summary(self, string: bool = True) -> dict[str, float | int] | str:
        totals = self._compute_totals()
        result = {}

        monetary_stats = {
            StatsCategory.INSURANCE_AMOUNT_BET,
            StatsCategory.INSURANCE_NET_WINNINGS,
            StatsCategory.AMOUNT_BET,
            StatsCategory.NET_WINNINGS,
            StatsCategory.TOTAL_AMOUNT_BET,
            StatsCategory.TOTAL_NET_WINNINGS
        }

        for category in StatsCategory:
            if category in monetary_stats:
                result[category.value] = totals.get(category.value, 0)
            else:
                result[category.value] = int(totals.get(category.value, 0))

        result[StatsCategory.TOTAL_AMOUNT_BET.value] = self._get_total(totals, StatsCategory.AMOUNT_BET, StatsCategory.INSURANCE_AMOUNT_BET)
        result[StatsCategory.TOTAL_NET_WINNINGS.value] = self._get_total(totals, StatsCategory.NET_WINNINGS, StatsCategory.INSURANCE_NET_WINNINGS)

        if string:
            monetary_stats_values = {stat.value for stat in monetary_stats}
            return '\n'.join(
                (f'{key}: ${value:,.2f}' if value >= 0 else f'{key}: -${abs(value):,.2f}')
                if key in monetary_stats_values else f'{key}: {value:,}'
                for key, value in result.items()
            )
        return result
