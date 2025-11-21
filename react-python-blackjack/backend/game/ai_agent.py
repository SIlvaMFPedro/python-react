from .game_engine import Hand, Card, Rank
from typing import Literal, Optional

Strategy = Literal['simple', 'basic', 'conservative']

class BlackJackAI:
    """
        AI Agent for Blackjack with multiple strategies:
        - Simple: Very basic decisions (hit on < 17, stand on >= 17)
        - Basic: Classic basic strategy from probability theory
        - Conservative: Risk-averse play focusing on not busting
    """
    def __init__(self, strategy: Strategy = 'basic'):
        self.strategy = strategy
        self.running_count = 0      # for card counting
        self.true_count = 0
        self.decks_remaining = 6

    def get_action(self,
                   player_hand: Hand,
                   dealer_up_card: Card,
                   can_double: bool = True,
                   can_split: bool = False,
                   can_surrender: bool = False) -> str:
        """
            Determine the best action based on strategy
            Returns: 'hit','stand','double','split' or 'surrender'
        """
        if self.strategy == 'simple':
            return self.simple_strategy(player_hand, dealer_up_card)
        elif self.strategy == 'basic':
            return self.basic_strategy(player_hand, dealer_up_card, can_double, can_split, can_surrender)
        elif self.strategy == 'conservative':
            return self.conservative_strategy(player_hand, dealer_up_card)
        else:
            return 'stand'

    def get_bet_size(self, base_bet: int, player_chips: int) -> int:
        """
            Determine bet size (with card counting for advanced strategies
        """
        if self.strategy == 'basic' and self.true_count > 2:
            # Increase bet when count is favorable
            multiplier = min(self.true_count - 1, 4)
            return min(base_bet * multiplier, player_chips, base_bet * 4)
        elif self.strategy == 'conservative':
            # Always bet minimum
            return min(base_bet, player_chips)
        else:
            return min(base_bet, player_chips)

    def should_buy_insurance(self, dealer_up_card: Card, player_hand: Hand) -> bool:
        """
            Decide whether to buy insurance when dealer shows Ace
        """
        if self.strategy == 'basic':
            # Only take insurance with high true count (card counting)
            return self.true_count >= 3
        else:
            # Generally bad bet - don't take insurance
            return False

    # -----------------------------
    #   STRATEGY IMPLEMENTATIONS
    # -----------------------------
    def simple_strategy(self,
                        player_hand: Hand,
                        dealer_up_card: Card) -> str:
        """
            Simple strategy: Hit on anything less than 17, stand on 17+
        """
        player_value = player_hand.value()
        if player_value < 17:
            return 'hit'
        else:
            return 'stand'

    def basic_strategy(self,
                       player_hand: Hand,
                       dealer_up_card: Card,
                       can_double: bool, can_split: bool, can_surrender: bool) -> str:
        """
            Basic strategy: - mathematically optimal play based on probability theory and computer simulations
        """
        player_value = player_hand.value()
        dealer_value = dealer_up_card.value()
        is_soft = player_hand.is_soft()
        is_pair = len(player_hand.cards) == 2 and player_hand.cards[0].value() == player_hand.cards[1].value()

        # Handle splits first
        if can_split and is_pair:
            pair_rank = player_hand.cards[0].rank
            # Always split Aces and 8s
            if pair_rank == Rank.ACE or pair_rank == Rank.EIGHT:
                return 'split'
            # Never split 5s and 10s
            if pair_rank == Rank.FIVE or pair_rank == Rank.TEN:
                pass    # fall through to regular strategy
            # Split 2s, 3s, 6s, 7s against dealer 2-7
            elif pair_rank in [Rank.TWO, Rank.THREE, Rank.SIX, Rank.SEVEN]:
                if 2 <= dealer_value <= 7:
                    return 'split'
            # Split 4s against dealer 5-6
            elif pair_rank == Rank.FOUR:
                if 5 <= dealer_value <= 6:
                    return 'split'
            # Split 9s against dealer 2-9 except 7
            elif pair_rank == Rank.NINE:
                if (2 <= dealer_value <= 6) or (8 <= dealer_value <= 9):
                    return 'split'
        # Handler surrender
        if can_surrender:
            # Surrender 16 against dealer 9, 10, Ace
            if player_value == 16 and dealer_value >= 9:
                return 'surrender'
            # surrender 15 against dealer 10
            if player_value == 15 and dealer_value == 10:
                return 'surrender'
        # Handle soft hands (with Ace counted as 11)
        if is_soft:
            # Soft 19+ always stand
            if player_value >= 19:
                return 'stand'
            # Soft 18
            elif player_value == 18:
                if dealer_value >= 9:
                    return 'hit'
                elif can_double and 3 <= dealer_value <= 6:
                    return 'double'
                else:
                    return 'stand'
            # Soft 17
            elif player_value == 17:
                if can_double and 3 <= dealer_value <= 6:
                    return 'double'
                else:
                    return 'hit'
            # Soft 13-16
            elif 13 <= player_value <= 16:
                if can_double and 5 <= dealer_value <= 6:
                    return 'double'
                else:
                    return 'hit'
            # Soft 12 or less
            else:
                return 'hit'
        # Handle hard hands
        else:
            # 17+ always stand
            if player_value >= 17:
                return 'stand'
            # 13-16: Stand against dealer 2-6, hit against 7+
            elif 13 <= player_value <= 16:
                if 2 <= dealer_value <= 6:
                    return 'stand'
                else:
                    return 'hit'
            # 12: Stand against dealer 4-6, hit otherwise
            elif player_value == 12:
                if 4 <= dealer_value <= 6:
                    return 'stand'
                else:
                    return 'hit'
            # 11: Always double if possible, otherwise hit
            elif player_value == 11:
                if can_double:
                    return 'double'
                else:
                    return 'hit'
            # 10: Double against dealer 2-9, hit against 10/Ace
            elif player_value == 10:
                if can_double and 2 <= dealer_value <= 9:
                    return 'double'
                else:
                    return 'hit'
            # 9: Double against dealer 3-6, hit otherwise
            elif player_value == 9:
                if can_double and 3 <= dealer_value <= 6:
                    return 'double'
                else:
                    return 'hit'
            # 8 or less: always hit
            else:
                return 'hit'

    def conservative_strategy(self,
                              player_hand: Hand,
                              dealer_up_card: Card,
                              can_double: bool, can_split: bool, can_surrender: bool) -> str:
        """
            Conservative strategy: Focus on not busting, play it safe
        """
        player_value = player_hand.value()
        dealer_value = dealer_up_card.value()
        is_soft = player_hand.is_soft()

        # Never split (too risky)
        # Never double (too risky)
        # Handle soft hands
        if is_soft:
            # Stand on soft 18+:
            if player_value >= 18:
                return 'stand'
            # Hit on soft 17 or less
            else:
                return 'hit'
        # Handle hard hands
        else:
            # Stand on 17+
            if player_value >= 17:
                return 'stand'
            # Stand on 12-16 if dealer shows weak card (2-6)
            elif 12 <= player_value <= 16:
                if 2 <= dealer_value <= 6:
                    return 'stand'
                # But stand on 15-16 even against 7-8 (conservative)
                elif player_value >= 15 and dealer_value <= 8:
                    return 'stand'
                else:
                    return 'hit'
            # Hit on 11 or less
            else:
                return 'hit'

    # -----------------------------
    #   CARD COUNTING FUNCTIONS
    # -----------------------------
    def update_count(self, card: Card):
        """
            Update running count for card counting (High-Low system)
        """
        if card.rank in [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX]:
            self.running_count += 1
        elif card.rank in [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]:
            self.running_count -= 1
        # 7,8 9s are neutral (0)

    def calculate_true_count(self, decks_remaining: float):
        """
            Calculate true count for betting decisions
        """
        if decks_remaining > 0:
            self.true_count = self.running_count / decks_remaining
        else:
            self.true_count = 0

    def reset_count(self):
        """
            Reset count when deck is reshuffled
        """
        self.running_count = 0
        self.true_count = 0


    # -----------------------------
    #       HELPER METHODS
    # -----------------------------
    def get_strategy_description(self) -> str:
        """
            Get description of current employed strategy
        """
        descriptions = {
            'simple': 'Simple strategy: Hit on <17, stand on 17+. Good for learning.',
            'basic': 'Basic strategy: Mathematically optimal play based on probability. Best for winning.',
            'conservative': 'Conservative strategy: Risk-averse, focuses on not busting. Safest play.',
        }
        return descriptions.get(self.strategy, 'Unknown strategy')

    def get_strategy_win_rate(self) -> float:
        """
            Approximate win rate for each strategy
        """
        win_rates = {
            'simple': 0.42,  # ~42% win rate
            'basic': 0.495,  # ~49.5% win rate (best)
            'conservative': 0.45,  # ~45% win rate
        }
        return win_rates.get(self.strategy, 0.40)




