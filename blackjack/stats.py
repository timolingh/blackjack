from collections import defaultdict
from dataclasses import dataclass
from blackjack.enums import StatsCategory
import pandas as pd


@dataclass(frozen=True)
class StatsKey:
    count : float | int | None
    category : StatsCategory


class Stats:
    """
    Represents a way to store blackjack statistics
    over the course of a simulation.

    """
    def __init__(self):
        self._stats = defaultdict(float)
        # For validation only - can uncomment to store list of values
        # self.hand_results_at_zero_count = list()

    @property
    def stats(self) -> defaultdict[str, float]:
        return self._stats

    def add_hand(self, count: float | int | None, category: StatsCategory) -> None:
        self._stats[StatsKey(count=count, category=category)] += 1
        self._stats[StatsKey(count=count, category=StatsCategory.TOTAL_HANDS_PLAYED)] += 1

    def add_value(self, count: float | int | None, category: StatsCategory, value: float | int = 1) -> None:
        self._stats[StatsKey(count=count, category=category)] += value

    def update_variance(self, count: float | int | None, value: float | int) -> None:
        delta = value - self._stats[StatsKey(count=count, category=StatsCategory.MEAN_EARNINGS_PER_HAND)]
        num_hands = self._stats[StatsKey(count=count, category=StatsCategory.TOTAL_HANDS_PLAYED)]
        self._stats[StatsKey(count=count, category=StatsCategory.MEAN_EARNINGS_PER_HAND)] += (delta / num_hands)

        ## Running variance using Welford's algorithm
        if num_hands == 1:
            self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_SUM_OF_SQUARED_DIFFERENCES)] = 0
            self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_VARIANCE)] = 0
            self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_STD_DEV)] = 0
        else:
            ## Note: delta_new is the diff between value and them UPDATED value for running mean.
            delta_new = value - self._stats[StatsKey(count=count, category=StatsCategory.MEAN_EARNINGS_PER_HAND)]
            sum_sq_update = delta * delta_new
            ## Update S using formula S_n = S_(n-1) + delta * delta_new
            self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_SUM_OF_SQUARED_DIFFERENCES)] += sum_sq_update
            self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_VARIANCE)] = (
                self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_SUM_OF_SQUARED_DIFFERENCES)] / (num_hands - 1)
            )
            self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_STD_DEV)] = (self._stats[StatsKey(count=count, category=StatsCategory.EARNINGS_VARIANCE)])**0.5

        ## for validation only - dont bother to group by count:
        ## uncomment to store individual hand results
        # if count == 0:
        #     self.hand_results_at_zero_count.append(value)

    def _compute_totals(self) -> defaultdict[str, float]:
        totals: defaultdict[str, float] = defaultdict(float)
        for stats_key, value in self._stats.items():
            totals[stats_key.category.value] += value
        return totals

    def _get_total(self, totals: defaultdict[str, float], *categories: StatsCategory) -> float:
        return sum(totals.get(category.value, 0) for category in categories)
    
    def _stats_dataframe(self) -> pd.DataFrame:
        stats_data = [
            {
                'count': key.count, 
                'category': key.category.name, 
                'value': value
            } 
            for key, value in self._stats.items()
        ]

        return pd.DataFrame(stats_data).pivot_table(
            index='count', columns='category', values='value', aggfunc='first'
        )
    
    def _compute_pooled_variance(self) -> dict:
        stats_data_frame = self._stats_dataframe()
        stats_data_frame = stats_data_frame.loc[stats_data_frame['TOTAL_HANDS_PLAYED'] > 1]
        weighted_variance = sum((stats_data_frame['TOTAL_HANDS_PLAYED'] - 1) * stats_data_frame['EARNINGS_VARIANCE'])
        degrees_of_freedom = sum(stats_data_frame['TOTAL_HANDS_PLAYED'] - 1)
        pooled_variance = weighted_variance / degrees_of_freedom
        earnings_std_dev = (pooled_variance)**0.5
        return {'pooled_variance': pooled_variance, 'earnings_std_dev': earnings_std_dev}

    def summary(self, string: bool = True) -> dict[str, float | int] | str:
        totals = self._compute_totals()
        variance_metrics = self._compute_pooled_variance()
        pooled_variance = variance_metrics['pooled_variance']
        earnings_std_dev = variance_metrics['earnings_std_dev']
        result = {}

        monetary_stats = {
            StatsCategory.INSURANCE_AMOUNT_BET,
            StatsCategory.INSURANCE_NET_WINNINGS,
            StatsCategory.AMOUNT_BET,
            StatsCategory.NET_WINNINGS,
            StatsCategory.TOTAL_AMOUNT_BET,
            StatsCategory.TOTAL_NET_WINNINGS
        }

        variance_stats = {
            StatsCategory.MEAN_EARNINGS_PER_HAND,
            StatsCategory.EARNINGS_SUM_OF_SQUARED_DIFFERENCES,
            StatsCategory.EARNINGS_VARIANCE,
            StatsCategory.POOLED_VARIANCE,
            StatsCategory.EARNINGS_STD_DEV
        }

        for category in StatsCategory:
            if category == StatsCategory.POOLED_VARIANCE:
                result[category.value] = pooled_variance
            if category == StatsCategory.EARNINGS_STD_DEV:
                result[category.value] = earnings_std_dev
            if category not in variance_stats:
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
