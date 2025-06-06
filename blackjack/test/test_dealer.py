def test_hole_card(dealer_with_hand):
    """Tests the hole_card method within the Dealer class."""
    assert dealer_with_hand.hole_card == '8'


def test_up_card(dealer_with_hand):
    """Tests the up_card method within the Dealer class."""
    assert dealer_with_hand.up_card == '6'


def test_reset_hand(dealer_with_hand):
    """Tests the reset_hand method within the Dealer class."""
    assert dealer_with_hand.hand.cards == ['8', '6']
    dealer_with_hand.reset_hand()
    assert dealer_with_hand.hand.cards == []
