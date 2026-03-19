from math import ceil, floor
from typing import Any

try:
    from typing import override  # Python >=3.11
except ImportError:  # pragma: no cover - fallback for older Python
    try:
        from typing_extensions import override  # type: ignore
    except ImportError:  # last resort: no-op decorator
        def override(func):
            return func
from blackjack.enums import CardCountingSystem
from blackjack.player import Player


class CardCounter(Player):
    """
    Represents an individual player at a table that
    counts cards according to a counting strategy.

    """
    def __init__(
        self,
        card_counting_system: CardCountingSystem,
        bet_ramp: dict[float | int, float | int],
        insurance: float | int | None = None,
        use_deviations: bool = False,
        **kwargs: Any
    ):
        """
        Parameters
        ----------
        card_counting_system
            Card counting system used by the player
        bet_ramp
            Dictionary where each key value is the running/true
            count and each value indicates the amount of money
            bet at that running/true count. In the event of a
            missing count, the amount of money bet is inferred
            from the previous running/true count
        insurance
            Minimum running or true count at which a player will
            purchase insurance, if desired, and if available
        use_deviations
            Whether this counter applies count-based deviations when acting

        """
        super().__init__(**kwargs)

        self.max_bet_ramp = max(bet_ramp.values())
        self.min_bet_ramp = min(bet_ramp.values())

        if self.max_bet_ramp > self.bankroll:
            raise ValueError(f"Maximum bet in {self.name}'s bet ramp exceeds their bankroll.")

        self.min_count = min(bet_ramp)
        self.max_count = max(bet_ramp)

        counts_to_check: list[float | int] = list(range(ceil(self.min_count), floor(self.max_count) + 1))
        if card_counting_system == CardCountingSystem.HALVES:
            counts_to_check.extend([count + 0.5 for count in range(floor(self.min_count), floor(self.max_count))])

        inferred_wager: float | int = 0
        for count in sorted(counts_to_check):
            if count not in bet_ramp:
                bet_ramp[count] = inferred_wager
            inferred_wager = bet_ramp[count]

        self._bet_ramp = bet_ramp
        self._card_counting_system = card_counting_system
        self._insurance = insurance
        self._use_deviations = use_deviations

    @property
    def card_counting_system(self) -> CardCountingSystem:
        return self._card_counting_system

    @property
    def bet_ramp(self) -> dict[float | int, float | int]:
        return self._bet_ramp

    @override
    def placed_bet(self, **kwargs: Any) -> float | int:
        count = kwargs['count']
        if count < self.min_count:
            return self._min_bet
        if count >= self.max_count:
            return self.max_bet_ramp
        return self._bet_ramp[count]

    @property
    def insurance(self) -> float | int | None:
        return self._insurance

    @property
    def use_deviations(self) -> bool:
        return self._use_deviations

    @override
    def decision(
        self,
        playing_strategy,
        hand,
        dealer_up_card,
        max_hands,
        running_count=None,
        true_count=None,
        can_surrender: bool = True,
        use_deviations: bool | None = None,
    ):
        # always prefer the player's configured setting unless an explicit override is given
        effective_use_deviations = self._use_deviations if use_deviations is None else use_deviations
        return super().decision(
            playing_strategy=playing_strategy,
            hand=hand,
            dealer_up_card=dealer_up_card,
            max_hands=max_hands,
            running_count=running_count,
            true_count=true_count,
            can_surrender=can_surrender,
            use_deviations=effective_use_deviations,
        )
