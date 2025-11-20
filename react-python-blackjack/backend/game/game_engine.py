from enum import Enum
from typing import List, Tuple, Optional
import random

class Suit(Enum):
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'

class Rank(Enum):
    ACE = 'A'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def value(self) -> int:
        """
            Get numeric value of a card
            (Ace - 11, Face cards - 10)
        """
        if self.rank == Rank.ACE:
            return 11
        elif self.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        else:
            return int(self.rank.value)

    def to_dict(self):
        """
            Get dictionary with all card related information
        """
        return {
            'suit': self.suit.value,
            'rank': self.rank.value,
            'value': self.value()
        }

    def __repr__(self):
        return f"{self.rank.value}{self.suit.value}"

class Deck:
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.cards: List[Card] = []
        self.reset()

    def reset(self):
        """
            Create and shuffle a fresh deck
        """
        self.cards = []
        for _ in range(self.num_decks):
            for suit in Suit:
                for rank in Rank:
                    self.cards.append(Card(suit, rank))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self) -> Card:
        """
            Deal one card from the deck
        """
        if len(self.cards) < 20:    # Reshuffle if deck is running low on cards
            self.reset()
        return self.cards.pop()

    def remaining(self) -> int:
        return len(self.cards)

class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.bet: int = 0
        self.is_split: bool = False
        self.is_doubled: bool = False
        self.is_surrendered: bool = False
        self.is_insured: bool = False

    def add_card(self, card: Card):
        self.cards.append(card)

    def value(self) -> int:
        """
            Calculate hand value (handling Aces as 1 or 11)
        """
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == Rank.ACE)
        # Convert aces from 11 to 1 if busted
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total

    def is_blackjack(self) -> bool:
        """
            Check if hand is a natural blackjack
        """
        return len(self.cards) == 2 and self.value() == 21

    def is_bust(self) -> bool:
        return self.value() > 21

    def is_soft(self) -> bool:
        """
            Check if hand has an Ace counted as 11
        """
        total = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == Rank.ACE)
        return aces > 0 and total <= 21 and (total - 10) < 12

    def can_split(self) -> bool:
        """
            Check if hand can be split
        """
        return len(self.cards) == 2 and self.cards[0].value()

    def can_double(self) -> bool:
        """
            Check if hand can be doubled
        """
        return len(self.cards) == 2 and not self.is_doubled

    def to_dict(self, hide_first: bool = False):
        """
            Converts hand to dictionary, optionally hiding the first card
        """
        cards_dict = []
        for i, card in enumerate(self.cards):
            if i == 0 and hide_first:
                cards_dict.append({'suit': '?', 'rank': '?', 'value': 0, 'hidden': True})
            else:
                cards_dict.append(card.to_dict())

        return {
            'cards': cards_dict,
            'value': 0 if hide_first else self.value(),
            'bet': self.bet,
            'is_blackjack': self.is_blackjack() if not hide_first else False,
            'is_bust': self.is_bust() if not hide_first else False,
            'is_soft': self.is_soft() if not hide_first else False,
            'can_split': self.can_split(),
            'can_double': self.can_double(),
            'is_surrendered': self.is_surrendered,
            'is_insured': self.is_insured
        }


class BlackJackGame:
    def __init__(self, num_decks: int = 6):
        self.deck = Deck(num_decks)
        self.player_hands: List[Hand] = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        self.game_phase = 'betting' # betting, playing, dealer_turn, finished
        self.player_chips = 1000
        self.current_bet = 0
        self.insurance_bet = 0

    def place_bet(self, amount: int) -> bool:
        """
            Place initial bet
        """
        if amount <= 0 or amount > self.player_chips:
            return False
        self.current_bet = amount
        self.player_chips -= amount
        return True

    def play_dealer_hand(self):
        """
            Dealer plays according to the rules (hit on 16, stand on 17)
        """
        while self.dealer_hand.value() < 17:
            self.dealer_hand.add_card(self.deck.deal())
        self.game_phase = 'finished'
        self.resolve_bets()

    def move_to_next_hand(self):
        """
            Move to next hand or dealer turn
        """
        self.current_hand_index += 1
        if self.current_hand_index >= len(self.player_hands):
            self.game_phase = 'dealer_turn'
            self.play_dealer_hand()

    def start_round(self):
        """
            Deal initial cards
        """
        if self.current_bet <= 0:
            return False
        self.player_hands = [Hand()]
        self.player_hands[0].bet = self.current_bet
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        # Deal initial cards
        self.player_hands[0].add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hands[0].add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.game_phase = 'playing'
        # Check for immediate blackjack
        if self.player_hands[0].is_blackjack():
            self.game_phase = 'dealer_turn'
            self.play_dealer_hand()
        return True

    def reset_round(self):
        """
            Reset for next round
        """
        self.player_hands = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        self.game_phase = 'betting'
        self.current_bet = 0
        self.insurance_bet = 0

    def resolve_bets(self):
        """
            Calculate winnings and update player chips
        """
        dealer_value = self.dealer_hand.value()
        dealer_blackjack = self.dealer_hand.is_blackjack()
        dealer_bust = self.dealer_hand.is_bust()
        # Resolve insurance
        if self.insurance_bet > 0:
            if dealer_blackjack:
                self.player_chips += self.insurance_bet * 3 # Insurance pays 2:1
            self.insurance_bet = 0
        # Resolve each hand
        for hand in self.player_hands:
            if hand.is_surrendered:
                continue
            hand_value = hand.value()
            if hand.is_bust():
                # Player bust - lose bet (already taken)
                pass
            elif hand.is_blackjack() and not dealer_blackjack:
                # Blackjack pays 3:2
                self.player_chips += hand.bet + int(hand.bet * 1.5)
            elif dealer_bust or hand_value > dealer_value:
                # Player wins
                self.player_chips += hand.bet * 2
            elif hand_value == dealer_value:
                # Push - return bet
                self.player_chips += hand.bet
            # else: dealer wins - lose bet (already taken)

    def hit(self) -> bool:
        """
            Player takes a card
        """
        if self.game_phase != 'playing':
            return False
        # Take a card and add it to current hand
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.add_card(self.deck.deal())
        if current_hand.is_bust():
            self.move_to_next_hand()
        return True

    def stand(self) -> bool:
        """
            Player stand on current hand
        """
        if self.game_phase != 'playing':
            return False
        self.move_to_next_hand()
        return True

    def double_down(self) -> bool:
        """
            Player doubles bet and takes one card
        """
        if self.game_phase != 'playing':
            return False
        # Check current hand and see if you can double
        current_hand = self.player_hands[self.current_hand_index]
        if not current_hand.can_double() or self.player_chips < current_hand.bet:
            return False
        # Double bet
        self.player_chips -= current_hand.bet
        current_hand.bet *= 2
        current_hand.is_doubled = True
        current_hand.add_card(self.deck.deal())
        self.move_to_next_hand()
        return True

    def split(self) -> bool:
        """
            Split current hand into two hands
        """
        if self.game_phase != 'playing':
            return False
        # Check current hand and see if you can split in two
        current_hand = self.player_hands[self.current_hand_index]
        if not current_hand.can_split() or self.player_chips < current_hand.bet:
            return False
        # Create new hand with second card
        new_hand = Hand()
        new_hand.bet = current_hand.bet
        new_hand.is_split = True
        new_hand.add_card(current_hand.cards.pop())
        # Deal new cards to both hands
        current_hand.add_card(self.deck.deal())
        new_hand.add_card(self.deck.deal())
        # Insert new hand after current
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
        self.player_chips -= current_hand.bet
        return True

    def surrender(self) -> bool:
        """
            Surrender and get half of your bet back
        """
        if self.game_phase != 'playing' or len(self.player_hands[self.current_hand_index].cards) != 2:
            return False
        # Check current hand
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.is_surrendered = True
        self.player_chips += current_hand.bet // 2
        self.move_to_next_hand()
        return True

    def buy_insurance(self) -> bool:
        """
            Buy insurance when dealer shows Ace
        """
        if self.game_phase != 'playing' or self.dealer_hand.cards[0].rank != Rank.ACE:
            return False
        # Fetch insurance amount
        insurance_amount = self.current_bet // 2
        if self.player_chips < insurance_amount:
            return False
        self.insurance_bet = insurance_amount
        self.player_chips -= insurance_amount
        self.player_hands[0].is_insured = True
        return True

    def get_state(self, hide_dealer_card: bool = True):
        """
            Get dictionary with current game state
        """
        return {
            'player_hands': [hand.to_dict() for hand in self.player_hands],
            'dealer_hand': self.dealer_hand.to_dict(hide_first=hide_dealer_card),
            'current_hand_index': self.current_hand_index,
            'game_phase': self.game_phase,
            'player_chips': self.player_chips,
            'current_bet': self.current_bet,
            'insurance_bet': self.current_bet,
            'deck_remaining': self.deck.remaining(),
        }