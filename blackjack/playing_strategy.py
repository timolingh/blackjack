from typing import Any

from blackjack.source.basic_strategy import H17_HARD_DICT, H17_SOFT_DICT, H17_PAIR_DICT
from blackjack.source.basic_strategy import S17_HARD_DICT, S17_SOFT_DICT, S17_PAIR_DICT


class PlayingStrategy:
    """
    Represents the decisions a player will make when faced with a
    pair split situation or a certain soft or hard count. Assumes the
    use of basic strategy.
    """

    def __init__(
        self,
        s17: bool,
        use_deviations: bool = False,
        deviations_levels: list[dict[str, Any]] | None = None,
    ):
        """
        Parameters
        ----------
        s17
            True if dealer stands on a soft 17, False otherwise
        use_deviations
            True to enable deviation lookups based on running/true count
        deviations_levels
            Optional list of deviation dictionaries to use; falls back to deviations.DEVIATION_LEVELS
        """
        if s17:
            self._hard_dict = S17_HARD_DICT
            self._soft_dict = S17_SOFT_DICT
            self._pair_dict = S17_PAIR_DICT
        else:
            self._hard_dict = H17_HARD_DICT
            self._soft_dict = H17_SOFT_DICT
            self._pair_dict = H17_PAIR_DICT

        self._use_deviations = use_deviations
        self._deviation_levels = self._load_deviation_levels(deviations_levels) if use_deviations else []

    def hard(
        self,
        total: int,
        dealer_up_card: str,
        running_count: float | int | None = None,
        true_count: float | int | None = None,
    ) -> str:
        decision = self._deviation_override(
            hand_type="hard",
            player_key=total,
            dealer_up_card=dealer_up_card,
            running_count=running_count,
            true_count=true_count,
        )
        if decision is None:
            decision = self._hard_dict[total][dealer_up_card]
        return self._resolve_decision(decision)

    def soft(
        self,
        total: int,
        dealer_up_card: str,
        running_count: float | int | None = None,
        true_count: float | int | None = None,
    ) -> str:
        decision = self._deviation_override(
            hand_type="soft",
            player_key=total,
            dealer_up_card=dealer_up_card,
            running_count=running_count,
            true_count=true_count,
        )
        if decision is None:
            decision = self._soft_dict[total][dealer_up_card]
        return self._resolve_decision(decision)

    def pair(
        self,
        card: str,
        dealer_up_card: str,
        running_count: float | int | None = None,
        true_count: float | int | None = None,
    ) -> str:
        decision = self._deviation_override(
            hand_type="pair",
            player_key=card,
            dealer_up_card=dealer_up_card,
            running_count=running_count,
            true_count=true_count,
        )
        if decision is None:
            decision = self._pair_dict[card][dealer_up_card]
        return self._resolve_decision(decision)

    def _resolve_decision(self, decision: str | dict) -> str:
        """Return the decision string, handling dict entries when present."""
        if isinstance(decision, dict):
            return self._handle_decision_dict(decision)
        return decision

    def _handle_decision_dict(self, decision_dict: dict) -> str:
        """Placeholder for future dict-based decision handling."""
        raise NotImplementedError("Dict-based player decisions are not implemented yet.")

    def _deviation_override(
        self,
        hand_type: str,
        player_key: Any,
        dealer_up_card: str,
        running_count: float | int | None,
        true_count: float | int | None,
    ) -> str | None:
        if not self._use_deviations:
            return None

        active = self._build_active_deviations(running_count=running_count, true_count=true_count)
        return active.get(hand_type, {}).get(player_key, {}).get(dealer_up_card)

    def _build_active_deviations(
        self,
        running_count: float | int | None,
        true_count: float | int | None,
    ) -> dict[str, dict]:
        if not self._deviation_levels:
            return {}

        levels_to_merge: list[dict[str, Any]] = []
        if running_count is not None and running_count > 0 and len(self._deviation_levels) >= 1:
            levels_to_merge.append(self._deviation_levels[0])

        if true_count is not None and len(self._deviation_levels) > 1:
            tc_floor = int(true_count)
            for idx in range(1, min(tc_floor, len(self._deviation_levels) - 1) + 1):
                levels_to_merge.append(self._deviation_levels[idx])

        merged: dict[str, dict] = {}
        for level in levels_to_merge:
            for hand_type, deviation_map in level.items():
                merged.setdefault(hand_type, {})
                for player_key, dealer_map in deviation_map.items():
                    merged[hand_type].setdefault(player_key, {})
                    merged[hand_type][player_key].update(dealer_map)

        return merged

    def _load_deviation_levels(self, overrides: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        if overrides is not None:
            return overrides
        try:
            from deviations import DEVIATION_LEVELS  # type: ignore
        except Exception:
            return []
        return DEVIATION_LEVELS
