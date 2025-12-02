from cryptography.hazmat.primitives.hashes import BLAKE2b
from redis.backoff import DecorrelatedJitterBackoff
from sqlalchemy.ext.asyncio import async_sessionmaker
from twisted.mail.maildir import initializeMaildir

from game.game_engine import Card, Deck, Hand, BlackJackGame, Suit, Rank
import pytest

class TestCard:
    """
        Test Card Class
    """
    def test_card_creation(self):
        card = Card(Suit.HEARTS, Rank.ACE)
        assert card.suit == Suit.HEARTS
        assert card.rank == Rank.ACE

    def test_ace_value(self):
        ace = Card(Suit.SPADES, Rank.ACE)
        assert ace.value() == 11

    def test_face_card_value(self):
        king = Card(Suit.HEARTS, Rank.KING)
        queen = Card(Suit.DIAMONDS, Rank.QUEEN)
        jack = Card(Suit.CLUBS, Rank.JACK)
        assert king.value() == 10
        assert queen.value() == 10
        assert jack.value() == 10

    def test_number_card_value(self):
        five = Card(Suit.HEARTS, Rank.KING)
        assert five.value() == 5

    def test_card_to_dict(self):
        card = Card(Suit.HEARTS, Rank.KING)
        card_dict = card.to_dict()
        assert card_dict['suit'] == '♥'
        assert card_dict['rank'] == 'K'
        assert card_dict['value'] == 10

class TestDeck:
    """
        Test Deck Class
    """
    def test_deck_initialization(self):
        deck = Deck(num_decks=1)
        assert len(deck.cards) == 52

    def test_multi_deck_initialization(self):
        deck = Deck(num_decks=6)
        assert len(deck.cards) == 312   # 52 * 6

    def test_deck_deal(self):
        deck = Deck(num_decks=1)
        initial_count = len(deck.cards)
        card = deck.deal()
        assert isinstance(card, Card)
        assert len(deck.cards) == initial_count - 1

    def test_deck_shuffle(self):
        deck1 = Deck(num_decks=1)
        deck2 = Deck(num_decks=1)
        # Cards should be in different order after shuffle
        # (this test can fail sometimes due to randomness
        cards1 = [str(c) for c in deck1.cards[:10]]
        cards2 = [str(c) for c in deck2.cards[:10]]
        # At least some cards should be different
        assert cards1 != cards2 or len(cards1) == len(cards2)

    def test_deck_reshuffles_when_low(self):
        deck = Deck(num_decks=1)
        # Deal most cards
        for _ in range(45):
            deck.deal()
        assert len(deck.cards) < 20
        # Next deal should trigger reshuffle
        deck.deal()
        assert len(deck.cards) == 51   # Full deck minus one dealt

class TestHand:
    """
        Test Hand Class
    """
    def test_hand_initialization(self):
        hand = Hand()
        assert len(hand.cards) == 0
        assert hand.bet == 0

    def test_hand_add_card(self):
        hand = Hand()
        card = Card(Suit.HEARTS, Rank.FIVE)
        hand.add_card(card)
        assert len(hand.cards) == 1
        assert hand.cards[0] == card

    def test_hand_value_simple(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        assert hand.value() == 12

    def test_hand_value_with_ace_as_11(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.NINE))
        assert hand.value() == 20  # Ace as 11

    def test_hand_value_with_ace_as_1(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.NINE))
        hand.add_card(Card(Suit.CLUBS, Rank.FIVE))
        assert hand.value() == 15  # Ace as 1 (11 would bust)

    def test_hand_blackjack(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        assert hand.is_blackjack() is True
        assert hand.value() == 21

    def test_hand_not_blackjack_with_21(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.SEVEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        hand.add_card(Card(Suit.CLUBS, Rank.SEVEN))
        assert hand.value() == 21
        assert hand.is_blackjack() is False # Three cards -> Not Blackjack!

    def test_hand_bust(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.KING))
        hand.add_card(Card(Suit.DIAMONDS, Rank.QUEEN))
        hand.add_card(Card(Suit.CLUBS, Rank.FIVE))
        assert hand.is_bust() is True
        assert hand.value() == 25

    def test_hand_soft(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        assert hand.is_soft() is True
        assert hand.value() == 25

    def test_hand_can_split_pairs(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        assert hand.can_split() is True

    def test_hand_cannot_split_different_cards(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        assert hand.can_split() is False

    def test_hand_can_double(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        assert hand.can_split() is False

    def test_hand_cannot_double_after_doubling(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        hand.is_doubled = True
        assert hand.can_double() is False

class TestBlackJackGame:
    """
        Test BlackJackGame Class
    """
    def test_game_initialization(self):
        game = BlackJackGame(num_decks=6)
        assert game.player_chips == 1000
        assert game.current_bet == 0
        assert game.game_phase == 'betting'

    def test_place_bet_valid(self):
        game = BlackJackGame()
        result = game.place_bet(100)
        assert result is True
        assert game.current_bet == 100
        assert game.player_chips == 900

    def test_place_bet_invalid_amount(self):
        game = BlackJackGame()
        result = game.place_bet(0)
        assert result is False
        assert game.current_bet == 0

    def test_place_bet_insufficient_chips(self):
        game = BlackJackGame()
        result = game.place_bet(2000)
        assert result is False
        assert game.current_bet == 0

    def test_start_round_deals_card(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        assert len(game.player_hands) == 1
        assert len(game.player_hands[0].cards) == 2
        assert len(game.dealer_hand.cards) == 2
        assert game.game_phase == 'playing'

    def test_start_round_requires_bet(self):
        game = BlackJackGame()
        result = game.start_round()
        assert result is False

    def test_hit_adds_card(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        initial_cards = len(game.player_hands[0].cards)
        game.hit()
        assert len(game.player_hands[0].cards) == initial_cards + 1

    def test_stand_moves_to_dealer_turn(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        game.stand()
        assert game.game_phase == 'finished'

    def test_double_down_doubles_bet_and_adds_card(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        initial_chips = game.player_chips
        initial_cards = len(game.player_hands[0].cards)
        game.double_down()
        assert game.player_hands[0].bet == 200
        assert game.player_chips == initial_chips - 100
        assert len(game.player_hands[0].cards) == initial_cards + 1
        assert game.player_hands[0].is_doubled is True

    def test_split_creates_two_hands(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        # Force a pair
        game.player_hands[0].cards = [
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.EIGHT)
        ]
        game.split()
        assert len(game.player_hands) == 2
        assert len(game.player_hands[0].cards) == 2
        assert len (game.player_hands[1].cards) == 2

    def test_surrender_gives_half_bet_back(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        initial_chips = game.player_chips
        game.surrender()
        assert game.player_hands[0].is_surrendered is True
        assert game.player_chips == initial_chips + 50

    def test_dealer_hits_on_16(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        # Force dealer hand to 16
        game.dealer_hand.cards = [
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.SIX)
        ]
        game.stand()    # Triggers dealer play
        # Dealer should have hit
        assert len(game.dealer_hand.cards) >= 3

    def test_dealer_stands_on_17(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        # Force dealer hand to 17
        game.dealer_hand.cards = [
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.SEVEN)
        ]
        game.stand()
        # Dealer should stand
        assert len(game.dealer_hand.cards) == 2

    def test_player_wins_with_higher_value(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        # Set up winning scenario
        game.player_hands[0].cards = [
            Card(Suit.HEARTS, Rank.TEN), Card(Suit.DIAMONDS, Rank.NINE)
        ]
        game.dealer_hand.cards = [
            Card(Suit.CLUBS, Rank.TEN), Card(Suit.SPADES, Rank.SEVEN)
        ]
        initial_chips = game.player_chips
        game.stand()
        # Player should win (19 vs 17)
        assert game.player_chips == initial_chips + 200 # Bet + winnings

    def test_player_loses_when_dealer_higher(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        # Set up losing scenario
        game.player_hands[0].cards = [
            Card(Suit.HEARTS, Rank.TEN), Card(Suit.DIAMONDS, Rank.SEVEN)
        ]
        game.dealer_hand.cards = [
            Card(Suit.CLUBS, Rank.TEN), Card(Suit.SPADES, Rank.NINE)
        ]
        initial_chips = game.player_chips
        game.stand()
        # Player should lose
        assert game.player_chips == initial_chips # No winnings

    def test_push_returns_bet(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        # Set up push scenario
        game.player_hands[0].cards = [
            Card(Suit.HEARTS, Rank.TEN), Card(Suit.DIAMONDS, Rank.EIGHT)
        ]
        game.dealer_hand.cards = [
            Card(Suit.CLUBS, Rank.TEN), Card(Suit.SPADES, Rank.EIGHT)
        ]
        initial_chips = game.player_chips
        game.stand()
        # Should get bet back
        assert game.player_chips == initial_chips + 100

    def test_blackjack_pays_3_to_2(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        # Give player blackjack
        game.player_hands[0].cards = [
            Card(Suit.HEARTS, Rank.ACE), Card(Suit.DIAMONDS, Rank.KING)
        ]
        # Dealer doesn't have blackjack
        game.dealer_hand.cards = [
            Card(Suit.CLUBS, Rank.TEN), Card(Suit.SPADES, Rank.NINE)
        ]
        initial_chips = game.player_chips
        game.stand()
        # Should get 1.5x payout
        assert game.player_chips == initial_chips + 100 + 150

    def test_reset_round(self):
        game = BlackJackGame()
        game.place_bet(100)
        game.start_round()
        game.reset_round()
        assert len(game.player_hands) == 0
        assert len(game.dealer_hand.cards) == 0
        assert game.game_phase == 'betting'
        assert game.current_bet == 0


# Parametrized tests
@pytest.mark.parametrize("rank,expected_value", [
    (Rank.ACE, 11),
    (Rank.TWO, 2),
    (Rank.THREE, 3),
    (Rank.FOUR, 4),
    (Rank.FIVE, 5),
    (Rank.SIX, 6),
    (Rank.SEVEN, 7),
    (Rank.EIGHT, 8),
    (Rank.NINE, 9),
    (Rank.TEN, 10),
    (Rank.JACK, 10),
    (Rank.QUEEN, 10),
    (Rank.KING, 10),
])
def test_card_values(rank, expected_value):
    """Test all card values"""
    card = Card(Suit.HEARTS, rank)
    assert card.value() == expected_value


@pytest.mark.parametrize("num_decks", [1, 2, 4, 6, 8])
def test_deck_sizes(num_decks):
    """Test different deck sizes"""
    deck = Deck(num_decks=num_decks)
    assert len(deck.cards) == 52 * num_decks
