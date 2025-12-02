from game.ai_agent import BlackJackAI
from game.game_engine import Hand, Card, Suit, Rank
import pytest


@pytest.fixture
def simple_ai():
    return BlackJackAI(strategy='simple')


@pytest.fixture
def basic_ai():
    return BlackJackAI(strategy='basic')


@pytest.fixture
def conservative_ai():
    return BlackJackAI(strategy='conservative')


class TestAIInitialization:
    """
        Test AI initialization
    """
    def test_simple_ai_initialization(self):
        ai = BlackJackAI(strategy='simple')
        assert ai.strategy == 'simple'

    def test_basic_ai_initialization(self):
        ai = BlackJackAI(strategy='basic')
        assert ai.strategy == 'basic'

    def test_conservative_ai_initialization(self):
        ai = BlackJackAI(strategy='conservative')
        assert ai.strategy == 'conservative'


class TestSimpleStrategy:
    """
        Test simple strategy decisions
    """
    def test_simple_hits_on_16(self, simple_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        dealer_card = Card(Suit.CLUBS, Rank.SEVEN)
        action = simple_ai.get_action(hand, dealer_card)
        assert action == 'hit'

    def test_simple_stands_on_17(self, simple_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        dealer_card = Card(Suit.CLUBS, Rank.SIX)
        action = simple_ai.get_action(hand, dealer_card)
        assert action == 'stand'

    def test_simple_stands_on_20(self, simple_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.QUEEN))
        dealer_card = Card(Suit.CLUBS, Rank.TEN)
        action = simple_ai.get_action(hand, dealer_card)
        assert action == 'stand'


class TestBasicStrategy:
    """
        Test basic strategy decisions
    """
    def test_basic_hits_12_vs_dealer_2(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TWO))
        dealer_card = Card(Suit.CLUBS, Rank.TWO)
        action = basic_ai.get_action(hand, dealer_card, can_double=False)
        assert action == 'hit'

    def test_basic_stands_12_vs_dealer_5(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TWO))
        dealer_card = Card(Suit.CLUBS, Rank.FIVE)
        action = basic_ai.get_action(hand, dealer_card, can_double=False)
        assert action == 'stand'

    def test_basic_doubles_11_vs_dealer_6(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.SIX))
        hand.add_card(Card(Suit.DIAMONDS, Rank.FIVE))
        dealer_card = Card(Suit.CLUBS, Rank.SIX)
        action = basic_ai.get_action(hand, dealer_card, can_double=True)
        assert action == 'double'

    def test_basic_hits_11_when_cannot_double(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.SIX))
        hand.add_card(Card(Suit.DIAMONDS, Rank.FIVE))
        dealer_card = Card(Suit.CLUBS, Rank.SIX)
        action = basic_ai.get_action(hand, dealer_card, can_double=False)
        assert action == 'hit'

    def test_basic_splits_aces(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.ACE))
        dealer_card = Card(Suit.CLUBS, Rank.SIX)
        action = basic_ai.get_action(hand, dealer_card, can_split=True)
        assert action == 'split'

    def test_basic_splits_eights(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        dealer_card = Card(Suit.CLUBS, Rank.TEN)
        action = basic_ai.get_action(hand, dealer_card, can_split=True)
        assert action == 'split'

    def test_basic_never_splits_tens(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TEN))
        dealer_card = Card(Suit.CLUBS, Rank.SIX)
        action = basic_ai.get_action(hand, dealer_card, can_split=True)
        assert action != 'split'

    def test_basic_surrenders_16_vs_dealer_10(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        dealer_card = Card(Suit.CLUBS, Rank.TEN)
        action = basic_ai.get_action(hand, dealer_card, can_surrender=True)
        assert action == 'surrender'

    def test_basic_stands_on_soft_19(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        dealer_card = Card(Suit.CLUBS, Rank.TEN)
        action = basic_ai.get_action(hand, dealer_card)
        assert action == 'stand'

    def test_basic_hits_soft_17(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        dealer_card = Card(Suit.CLUBS, Rank.TEN)
        action = basic_ai.get_action(hand, dealer_card, can_double=False)
        assert action == 'hit'


class TestConservativeStrategy:
    """
        Test conservative strategy decisions
    """
    def test_conservative_stands_on_12_vs_weak_dealer(self, conservative_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TWO))
        dealer_card = Card(Suit.CLUBS, Rank.FIVE)
        action = conservative_ai.get_action(hand, dealer_card, can_double=False)
        assert action == 'stand'

    def test_conservative_never_splits(self, conservative_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        dealer_card = Card(Suit.CLUBS, Rank.SIX)
        action = conservative_ai.get_action(hand, dealer_card, can_split=True)
        assert action != 'split'

    def test_conservative_never_doubles(self, conservative_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.SIX))
        hand.add_card(Card(Suit.DIAMONDS, Rank.FIVE))
        dealer_card = Card(Suit.CLUBS, Rank.SIX)
        action = conservative_ai.get_action(hand, dealer_card, can_double=True)
        assert action != 'double'


class TestBettingDecisions:
    """
        Test AI betting logic
    """
    def test_simple_bets_minimum(self, simple_ai):
        bet = simple_ai.get_bet_size(base_bet=25, player_chips=1000)
        assert bet == 25

    def test_conservative_bets_minimum(self, conservative_ai):
        bet = conservative_ai.get_bet_size(base_bet=25, player_chips=1000)
        assert bet == 25

    def test_basic_increases_bet_with_positive_count(self, basic_ai):
        basic_ai.true_count = 3
        bet = basic_ai.get_bet_size(base_bet=25, player_chips=1000)
        assert bet > 25  # Should increase bet

    def test_bet_size_respects_chip_limit(self, basic_ai):
        basic_ai.true_count = 5
        bet = basic_ai.get_bet_size(base_bet=25, player_chips=50)
        assert bet <= 50  # Should not exceed available chips


class TestInsuranceDecisions:
    """
        Test insurance decisions
    """
    def test_simple_rejects_insurance(self, simple_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TEN))
        dealer_card = Card(Suit.CLUBS, Rank.ACE)
        should_insure = simple_ai.should_buy_insurance(dealer_card, hand)
        assert should_insure is False

    def test_basic_takes_insurance_with_high_count(self, basic_ai):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TEN))
        dealer_card = Card(Suit.CLUBS, Rank.ACE)
        basic_ai.true_count = 4
        should_insure = basic_ai.should_buy_insurance(dealer_card, hand)
        assert should_insure is True


class TestCardCounting:
    """
        Test card counting logic
    """
    def test_counting_low_cards(self, basic_ai):
        basic_ai.running_count = 0
        basic_ai.update_count(Card(Suit.HEARTS, Rank.TWO))
        assert basic_ai.running_count == 1
        basic_ai.update_count(Card(Suit.DIAMONDS, Rank.FIVE))
        assert basic_ai.running_count == 2

    def test_counting_high_cards(self, basic_ai):
        basic_ai.running_count = 0
        basic_ai.update_count(Card(Suit.HEARTS, Rank.TEN))
        assert basic_ai.running_count == -1
        basic_ai.update_count(Card(Suit.DIAMONDS, Rank.ACE))
        assert basic_ai.running_count == -2

    def test_counting_neutral_cards(self, basic_ai):
        basic_ai.running_count = 0
        basic_ai.update_count(Card(Suit.HEARTS, Rank.SEVEN))
        assert basic_ai.running_count == 0
        basic_ai.update_count(Card(Suit.DIAMONDS, Rank.EIGHT))
        assert basic_ai.running_count == 0

    def test_true_count_calculation(self, basic_ai):
        basic_ai.running_count = 12
        basic_ai.calculate_true_count(decks_remaining=3)
        assert basic_ai.true_count == 4  # 12 / 3

    def test_reset_count(self, basic_ai):
        basic_ai.running_count = 10
        basic_ai.true_count = 5
        basic_ai.reset_count()
        assert basic_ai.running_count == 0
        assert basic_ai.true_count == 0


class TestStrategyDescriptions:
    """
        Test strategy descriptions and metadata
    """
    def test_simple_description(self, simple_ai):
        desc = simple_ai.get_strategy_description()
        assert 'Simple' in desc or 'simple' in desc

    def test_basic_description(self, basic_ai):
        desc = basic_ai.get_strategy_description()
        assert 'Basic' in desc or 'basic' in desc

    def test_conservative_description(self, conservative_ai):
        desc = conservative_ai.get_strategy_description()
        assert 'Conservative' in desc or 'conservative' in desc

    def test_win_rates(self):
        simple_ai = BlackJackAI(strategy='simple')
        basic_ai = BlackJackAI(strategy='basic')
        conservative_ai = BlackJackAI(strategy='conservative')
        # Basic strategy should have the highest win rate
        assert basic_ai.get_strategy_win_rate() > simple_ai.get_strategy_win_rate()
        assert basic_ai.get_strategy_win_rate() > conservative_ai.get_strategy_win_rate()


# Integration test
def test_ai_plays_complete_game():
    """
        Test AI can play through a complete game without errors
    """
    from game.game_engine import BlackJackGame
    game = BlackJackGame(num_decks=6)
    ai = BlackJackAI(strategy='basic')
    # Play 10 hands
    for _ in range(10):
        # AI places bet
        bet = ai.get_bet_size(25, game.player_chips)
        if game.place_bet(bet):
            game.start_round()
            # AI plays hand
            while game.game_phase == 'playing':
                current_hand = game.player_hands[game.current_hand_index]
                dealer_up_card = game.dealer_hand.cards[0]
                action = ai.get_action(
                    current_hand,
                    dealer_up_card,
                    can_double=current_hand.can_double(),
                    can_split=current_hand.can_split()
                )
                if action == 'hit':
                    if not game.hit():
                        break
                elif action == 'stand':
                    if not game.stand():
                        break
                elif action == 'double':
                    if not game.double_down():
                        game.hit()
                elif action == 'split':
                    if not game.split():
                        game.hit()
                else:
                    break
            game.reset_round()
    # Should still have chips (or at least finished without errors)
    assert game.player_chips >= 0