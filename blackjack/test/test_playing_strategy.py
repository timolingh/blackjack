def test_hard_h17(playing_strategy_h17):
    """
    Tests the hard method within the PlayingStrategy class
    when the dealer hits on a soft 17.

    """
    assert playing_strategy_h17.hard(total=11, dealer_up_card='A') == 'Dh'


def test_soft_h17(playing_strategy_h17):
    """
    Tests the soft method within the PlayingStrategy class
    when the dealer hits on a soft 17.

    """
    assert playing_strategy_h17.soft(total=19, dealer_up_card='6') == 'Ds'


def test_pair_h17(playing_strategy_h17):
    """
    Tests the pair method within the PlayingStrategy class
    when the dealer hits on a soft 17.

    """
    assert playing_strategy_h17.pair(card='8', dealer_up_card='A') == 'P'


def test_surrender_h17_only_16v_high_cards(playing_strategy_h17):
    """Verify H17 surrender map: 16 vs 9/10/A surrender, 15 only vs 10."""
    assert playing_strategy_h17.hard(total=16, dealer_up_card='9') == 'Rh'
    assert playing_strategy_h17.hard(total=16, dealer_up_card='10') == 'Rh'
    assert playing_strategy_h17.hard(total=16, dealer_up_card='A') == 'Rh'
    assert playing_strategy_h17.hard(total=15, dealer_up_card='10') == 'Rh'
    assert playing_strategy_h17.hard(total=15, dealer_up_card='J') == 'Rh'
    assert playing_strategy_h17.hard(total=15, dealer_up_card='Q') == 'Rh'
    assert playing_strategy_h17.hard(total=15, dealer_up_card='K') == 'Rh'
    assert playing_strategy_h17.hard(total=15, dealer_up_card='9') == 'H'
    assert playing_strategy_h17.hard(total=15, dealer_up_card='A') == 'H'


def test_hard_s17(playing_strategy_s17):
    """
    Tests the hard method within the PlayingStrategy class
    when the dealer stands on a soft 17.

    """
    assert playing_strategy_s17.hard(total=11, dealer_up_card='A') == 'H'


def test_soft_s17(playing_strategy_s17):
    """
    Tests the soft method within the PlayingStrategy class
    when the dealer stands on a soft 17.

    """
    assert playing_strategy_s17.soft(total=19, dealer_up_card='6') == 'S'


def test_pair_s17(playing_strategy_s17):
    """
    Tests the pair method within the PlayingStrategy class
    when the dealer stands on a soft 17.

    """
    assert playing_strategy_s17.pair(card='8', dealer_up_card='A') == 'P'


def test_deviation_running_count_positive_stand_16v10(playing_strategy_deviations_h17):
    """Running count > 0 should still surrender 16 vs 10 when surrender is available."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='10', running_count=1, true_count=None
    )
    assert decision == 'Rh'


def test_deviation_true_count_double_11vA(playing_strategy_deviations_h17):
    """True count >= 1 triggers double 11 vs Ace."""
    decision = playing_strategy_deviations_h17.hard(
        total=11, dealer_up_card='A', running_count=0, true_count=1
    )
    assert decision == 'Dh'


def test_deviation_true_count_soft19v5(playing_strategy_deviations_h17):
    """True count >= 1 triggers double soft 19 vs 5."""
    decision = playing_strategy_deviations_h17.soft(
        total=19, dealer_up_card='5', running_count=0, true_count=1
    )
    assert decision == 'Ds'


def test_deviation_true_count_soft17v2(playing_strategy_deviations_h17):
    """True count >= 1 triggers double soft 17 vs 2."""
    decision = playing_strategy_deviations_h17.soft(
        total=17, dealer_up_card='2', running_count=0, true_count=1
    )
    assert decision == 'Ds'


def test_deviation_tc4_split_tens_vs6(playing_strategy_deviations_h17):
    """TC >= 4 enables splitting 10s vs 6."""
    decision = playing_strategy_deviations_h17.pair(
        card='10', dealer_up_card='6', running_count=0, true_count=4
    )
    assert decision == 'P'


def test_deviation_tc5_split_tens_vs5(playing_strategy_deviations_h17):
    """TC >= 5 enables splitting 10s vs 5."""
    decision = playing_strategy_deviations_h17.pair(
        card='10', dealer_up_card='5', running_count=0, true_count=5
    )
    assert decision == 'P'


def test_deviation_tc6_split_tens_vs4(playing_strategy_deviations_h17):
    """TC >= 6 enables splitting 10s vs 4."""
    decision = playing_strategy_deviations_h17.pair(
        card='10', dealer_up_card='4', running_count=0, true_count=6
    )
    assert decision == 'P'


def test_negative_running_count_override_applies():
    """Negative running/true counts use negative deviation tiers."""
    custom_levels = {
        "positive": [],
        "negative": [
            {"hard": {12: {"4": "H"}}, "soft": {}, "pair": {}},  # RC < 0
            {"hard": {13: {"2": "H"}}, "soft": {}, "pair": {}},  # TC <= -1
        ],
    }
    ps = PlayingStrategy(s17=False, use_deviations=True, deviations_levels=custom_levels)

    decision_rc = ps.hard(total=12, dealer_up_card='4', running_count=-1, true_count=None)
    assert decision_rc == 'H'

    decision_tc = ps.hard(total=13, dealer_up_card='2', running_count=-1, true_count=-2)
    assert decision_tc == 'H'


def test_negative_rc_soft19v6_stand_tc_zero(playing_strategy_deviations_h17):
    """RC < 0 with TC = 0 should apply negative base: soft 19 vs 6 stands."""
    decision = playing_strategy_deviations_h17.soft(
        total=19, dealer_up_card='6', running_count=-1, true_count=0
    )
    assert decision == 'S'


def test_positive_rc_tc_zero_uses_positive_base(playing_strategy_deviations_h17):
    """RC > 0 with TC = 0 uses positive base; 15 vs A should surrender."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=1, true_count=0
    )
    assert decision == 'Rh'


def test_positive_rc_tc_zero_hard16v10(playing_strategy_deviations_h17):
    """RC > 0 with TC = 0: hard 16 vs 10 should surrender when surrender is allowed."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='10', running_count=1, true_count=0
    )
    assert decision == 'Rh'


def test_h17_16v8_basic_hits_with_surrender(playing_strategy_h17):
    """Baseline: 16 vs 8 should hit when surrender is available (no count)."""
    assert playing_strategy_h17.hard(total=16, dealer_up_card='8', can_surrender=True) == 'H'


def test_tc4_h17_16v8_surrender_if_allowed(playing_strategy_deviations_h17):
    """TC >= 4: hard 16 vs 8 should surrender when surrender is available."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='8', running_count=0, true_count=4, can_surrender=True
    )
    assert decision == 'Rh'


def test_tc4_h17_16v8_hit_if_no_surrender(playing_strategy_deviations_h17):
    """TC >= 4: hard 16 vs 8 should hit when surrender is unavailable."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='8', running_count=0, true_count=4, can_surrender=False
    )
    assert decision == 'H'


def test_h17_16v9_surrender_basic(playing_strategy_deviations_h17):
    """Default: hard 16 vs 9 should surrender when surrender is available."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='9', running_count=0, true_count=0, can_surrender=True
    )
    assert decision == 'Rh'


def test_h17_16v9_hit_when_tc_negative(playing_strategy_deviations_h17):
    """TC <= -1 deviation: hard 16 vs 9 should hit even with surrender available."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='9', running_count=-1, true_count=-1, can_surrender=True
    )
    assert decision == 'H'


def test_h17_16v9_hit_when_no_surrender(playing_strategy_deviations_h17):
    """No surrender available: hard 16 vs 9 should hit by default."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='9', running_count=0, true_count=0, can_surrender=False
    )
    assert decision == 'H'


def test_h17_16v9_stand_tc4_no_surrender(playing_strategy_deviations_h17):
    """Post-hit TC >= 4 deviation: hard 16 vs 9 should stand when surrender is unavailable."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='9', running_count=1, true_count=4, can_surrender=False
    )
    assert decision == 'S'


def test_h17_16vA_surrender_basic(playing_strategy_deviations_h17):
    """Baseline: hard 16 vs A should surrender when surrender is available."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='A', running_count=0, true_count=0, can_surrender=True
    )
    assert decision == 'Rh'


def test_h17_16vA_hit_no_surrender(playing_strategy_deviations_h17):
    """No surrender available: hard 16 vs A should hit by basic strategy."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='A', running_count=0, true_count=0, can_surrender=False
    )
    assert decision == 'H'


def test_h17_16vA_stand_tc3_no_surrender(playing_strategy_deviations_h17):
    """Post-hit TC >= 3 deviation: hard 16 vs A should stand when surrender is unavailable."""
    decision = playing_strategy_deviations_h17.hard(
        total=16, dealer_up_card='A', running_count=1, true_count=3, can_surrender=False
    )
    assert decision == 'S'


def test_h17_15v9_hit_basic(playing_strategy_deviations_h17):
    """Baseline: hard 15 vs 9 hits."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='9', running_count=0, true_count=0, can_surrender=True
    )
    assert decision == 'H'


def test_h17_15v9_hit_tc2_with_surrender(playing_strategy_deviations_h17):
    """TC >= 2 with surrender available: hard 15 vs 9 should surrender per deviation."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='9', running_count=0, true_count=2, can_surrender=True
    )
    assert decision == 'Rh'


def test_h17_15vA_surrender_tc_minus1(playing_strategy_deviations_h17):
    """TC = -1: hard 15 vs A should surrender when surrender is available."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=0, true_count=-1, can_surrender=True
    )
    assert decision == 'Rh'


def test_h17_15vA_surrender_tc_zero(playing_strategy_deviations_h17):
    """TC = 0: hard 15 vs A should surrender when surrender is available."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=1, true_count=0, can_surrender=True
    )
    assert decision == 'Rh'


def test_h17_15vA_surrender_tc_positive(playing_strategy_deviations_h17):
    """TC > 0: hard 15 vs A should surrender when surrender is available."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=1, true_count=2, can_surrender=True
    )
    assert decision == 'Rh'


def test_h17_15vA_hit_no_surrender(playing_strategy_deviations_h17):
    """No surrender: hard 15 vs A should hit by default."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=0, true_count=0, can_surrender=False
    )
    assert decision == 'H'


def test_h17_15vA_stand_tc5_no_surrender(playing_strategy_deviations_h17):
    """No surrender: TC >= 5 deviation should stand 15 vs A."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=1, true_count=5, can_surrender=False
    )
    assert decision == 'S'


def test_negative_rc_tc_zero_hard16v10(playing_strategy_deviations_h17):
    """Post-hit context RC < 0, TC = 0: hard 16 vs 10 should hit (surrender unavailable)."""
    decision = playing_strategy_deviations_h17.hard(
        total=16,
        dealer_up_card='10',
        running_count=-1,
        true_count=0,
        can_surrender=False,
    )
    assert decision == 'H'


def test_negative_rc_tc_zero_hard15vA(playing_strategy_deviations_h17):
    """RC < 0 with TC = 0 still surrenders 15 vs A (from positive base merged)."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=-1, true_count=0
    )
    assert decision == 'Rh'


def test_tc_minus_one_merges_both_bases(playing_strategy_deviations_h17):
    """TC = -1 merges positive and negative bases; 15 vs A surrender still applies."""
    decision = playing_strategy_deviations_h17.hard(
        total=15, dealer_up_card='A', running_count=-1, true_count=-1
    )
    assert decision == 'Rh'


def test_post_hit_positive_tc3_stand_16vA():
    """Post-hit: TC >= 3 should stand 16 vs A (positive post-hit tier)."""
    from blackjack.deviations import DEVIATION_LEVELS, NEGATIVE_DEVIATION_LEVELS, POST_HIT_DEVIATION_LEVELS
    levels = {
        "positive": DEVIATION_LEVELS,
        "negative": NEGATIVE_DEVIATION_LEVELS,
    }
    ps = PlayingStrategy(
        s17=False,
        use_deviations=True,
        deviations_levels=levels,
        post_hit_deviations=POST_HIT_DEVIATION_LEVELS,
    )
    decision = ps.hard(total=16, dealer_up_card='A', running_count=1, true_count=3, can_surrender=False)
    assert decision == 'S'


def test_post_hit_positive_tc4_stand_16v9():
    """Post-hit: TC >= 4 should stand 16 vs 9 (positive post-hit tier)."""
    from blackjack.deviations import DEVIATION_LEVELS, NEGATIVE_DEVIATION_LEVELS, POST_HIT_DEVIATION_LEVELS
    levels = {
        "positive": DEVIATION_LEVELS,
        "negative": NEGATIVE_DEVIATION_LEVELS,
    }
    ps = PlayingStrategy(
        s17=False,
        use_deviations=True,
        deviations_levels=levels,
        post_hit_deviations=POST_HIT_DEVIATION_LEVELS,
    )
    decision = ps.hard(total=16, dealer_up_card='9', running_count=1, true_count=4, can_surrender=False)
    assert decision == 'S'


def test_post_hit_positive_tc4_stand_15v10():
    """Post-hit: TC >= 4 should stand 15 vs 10."""
    from blackjack.deviations import DEVIATION_LEVELS, NEGATIVE_DEVIATION_LEVELS, POST_HIT_DEVIATION_LEVELS
    levels = {
        "positive": DEVIATION_LEVELS,
        "negative": NEGATIVE_DEVIATION_LEVELS,
    }
    ps = PlayingStrategy(
        s17=False,
        use_deviations=True,
        deviations_levels=levels,
        post_hit_deviations=POST_HIT_DEVIATION_LEVELS,
    )
    decision = ps.hard(total=15, dealer_up_card='10', running_count=1, true_count=4, can_surrender=False)
    assert decision == 'S'


def test_post_hit_positive_tc5_stand_15vA():
    """Post-hit: TC >= 5 should stand 15 vs A."""
    from blackjack.deviations import DEVIATION_LEVELS, NEGATIVE_DEVIATION_LEVELS, POST_HIT_DEVIATION_LEVELS
    levels = {
        "positive": DEVIATION_LEVELS,
        "negative": NEGATIVE_DEVIATION_LEVELS,
    }
    ps = PlayingStrategy(
        s17=False,
        use_deviations=True,
        deviations_levels=levels,
        post_hit_deviations=POST_HIT_DEVIATION_LEVELS,
    )
    decision = ps.hard(total=15, dealer_up_card='A', running_count=1, true_count=5, can_surrender=False)
    assert decision == 'S'
from blackjack.playing_strategy import PlayingStrategy
