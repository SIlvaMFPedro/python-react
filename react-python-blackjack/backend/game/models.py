from email.policy import default
from tkinter.constants import CASCADE

from django.contrib.auth.models import User
from django.db import models

# -----------------------------
#   BLACKJACK GAME MODELS
# -----------------------------
class BlackJackGameSession(models.Model):
    """
        Blackjack game session
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    starting_chips = models.IntegerField(default=1000)
    ending_chips = models.IntegerField(default=0)
    hands_played = models.IntegerField(default=0)
    hands_won = models.IntegerField(default=0)
    hands_lost = models.IntegerField(default=0)
    hands_pushed = models.IntegerField(default=0)
    blackjacks = models.IntegerField(default=0)
    busts = models.IntegerField(default=0)
    total_wagered = models.IntegerField(default=0)
    net_winnings = models.IntegerField(default=0)
    ai_mode = models.BooleanField(default=False)
    ai_strategy = models.CharField(max_length=20, null=True, blank=True)
    duration = models.IntegerField(default=0)   # seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Blackjack Session {self.id} with {self.hands_played} hands played"

    @property
    def win_rate(self):
        if self.hands_played > 0:
            return (self.hands_won / self.hands_played) * 100
        return 0

    @property
    def profit(self):
        return self.ending_chips - self.starting_chips

class BlackJackHand(models.Model):
    """
        Individual blackjack hand history
    """
    sessions = models.ForeignKey(BlackJackGameSession, on_delete=models.CASCADE, related_name='hands')
    hand_number = models.IntegerField()
    # Player data
    player_cards = models.JSONField()   # List of card dictionaries
    player_value = models.IntegerField()
    player_bet = models.IntegerField()
    player_blackjack = models.BooleanField(default=False)
    player_bust = models.BooleanField(default=False)
    # Dealer data
    dealer_cards = models.JSONField()   # List of card dictionaries
    dealer_value = models.IntegerField()
    dealer_blackjack = models.BooleanField(default=False)
    dealer_bust = models.BooleanField(default=False)
    # Result
    result = models.CharField(max_length=20)    # 'win', 'lose', 'push', 'blackjack', 'surrender'
    payout = models.IntegerField()
    # Actions taken
    actions = models.JSONField(default=list)    # ['hit', 'stand', 'double', 'split', 'surrender', 'insurance']
    was_split = models.BooleanField(default=False)
    was_doubled = models.BooleanField(default=False)
    was_surrendered = models.BooleanField(default=False)
    had_insurance = models.BooleanField(default=False)
    # Model creation date
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['hand_number']

    def __str__(self):
        return f"Hand {self.hand_number} - {self.result.upper()}"


class PlayerStatistics(models.Model):
    """
        Overall player statistics across all sessions
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Totals
    total_sessions = models.IntegerField(default=0)
    total_hands = models.IntegerField(default=0)
    total_wagered = models.IntegerField(default=0)
    total_won = models.IntegerField(default=0)
    net_profit = models.IntegerField(default=0)
    # Wins & Losses
    hands_won = models.IntegerField(default=0)
    hands_lost = models.IntegerField(default=0)
    hands_pushed = models.IntegerField(default=0)
    blackjacks = models.IntegerField(default=0)
    busts = models.IntegerField(default=0)
    # Streaks
    current_streak = models.IntegerField(default=0) # Positive = winning, negative = losing
    longest_win_streak = models.IntegerField(default=0)
    longest_lose_streak = models.IntegerField(default=0)
    # Bests
    biggest_win = models.IntegerField(default=0)
    biggest_loss = models.IntegerField(default=0)
    highest_chips = models.IntegerField(default=0)
    # AI Stats
    ai_hands_played = models.IntegerField(default=0)
    ai_hands_won = models.IntegerField(default=0)
    # Model update date
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Stats"

    @property
    def win_rate(self):
        if self.total_hands > 0:
            return (self.hands_won / self.total_hands) * 100
        return 0

    @property
    def return_on_investment(self):
        if self.total_wagered > 0:
            return (self.net_profit / self.total_wagered) * 100
        return 0

class Achievement(models.Model):
    """
        Player Achievements
        Examples:
            - "First Win" - Win your first hand
            - "Blackjack Master" - Get 10 blackjacks
            - "Lucky Streak" - Win 5 hands in a row
            - "High Roller" - Bet $500 in a single hand
            - "Card Counter" - Win 100 hands with AI
            - "Risk Taker" - Win after doubling down 20 times
            - "Survivor" - Play 100 hands without going broke
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.TextField()
    icon = models.CharField(max_length=50)  # 'winning', 'playing', 'special'
    # Achievement unlocked date
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-unlocked_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"