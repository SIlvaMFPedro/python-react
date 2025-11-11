from game.models import GameSession, HighScore
from django.contrib.auth.models import User
import pytest

@pytest.mark.django_db
class TestGameSessionModel:
    """
        Test GameSession model
    """
    def test_create_game_session(self):
        session = GameSession.objects.create(
            score=100,
            moves=50,
            duration=120,
            ai_mode=False
        )
        assert session.score == 100
        assert session.moves == 50
        assert session.duration == 120
        assert session.ai_mode is False

    def test_game_session_with_user(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        session = GameSession.objects.create(
            user=user,
            score=150,
            moves=75,
            duration=180,
            ai_mode=True
        )
        assert session.user == user
        assert session.ai_mode is True

    def test_game_session_without_user(self):
        session = GameSession.objects.create(
            score=50,
            moves=25,
            duration=60
        )
        assert session.user is None

    def test_game_session_default_values(self):
        session = GameSession.objects.create()
        assert session.score == 0
        assert session.moves == 0
        assert session.duration == 0
        assert session.ai_mode is False

    def test_game_session_ordering(self):
        GameSession.objects.create(score=100)
        GameSession.objects.create(score=200)
        GameSession.objects.create(score=150)

        sessions = GameSession.objects.all()
        assert sessions[0].score == 200  # Highest score first
        assert sessions[1].score == 150
        assert sessions[2].score == 100

    def test_game_session_str_representation(self):
        session = GameSession.objects.create(score=100)
        str_repr = str(session)
        assert 'Score: 100' in str_repr

    def test_game_session_created_at(self):
        session = GameSession.objects.create(score=100)
        assert session.created_at is not None

    def test_multiple_sessions_per_user(self):
        user = User.objects.create_user(username='player', password='pass')
        GameSession.objects.create(user=user, score=100)
        GameSession.objects.create(user=user, score=150)
        GameSession.objects.create(user=user, score=200)
        user_sessions = GameSession.objects.filter(user=user)
        assert user_sessions.count() == 3


@pytest.mark.django_db
class TestHighScoreModel:
    """
        Test HighScore model
    """
    def test_create_high_score(self):
        high_score = HighScore.objects.create(
            username='Player1',
            score=500
        )
        assert high_score.username == 'Player1'
        assert high_score.score == 500

    def test_high_score_with_user(self):
        user = User.objects.create_user(username='champion', password='pass')
        high_score = HighScore.objects.create(
            user=user,
            username=user.username,
            score=1000
        )
        assert high_score.user == user
        assert high_score.username == 'champion'

    def test_high_score_default_username(self):
        high_score = HighScore.objects.create(score=300)
        assert high_score.username == 'Anonymous'

    def test_high_score_ordering(self):
        HighScore.objects.create(username='Player1', score=100)
        HighScore.objects.create(username='Player2', score=500)
        HighScore.objects.create(username='Player3', score=300)
        scores = HighScore.objects.all()
        assert scores[0].score == 500  # Highest first
        assert scores[1].score == 300
        assert scores[2].score == 100

    def test_high_score_str_representation(self):
        high_score = HighScore.objects.create(username='TestPlayer', score=250)
        str_repr = str(high_score)
        assert 'TestPlayer' in str_repr
        assert '250' in str_repr

    def test_high_score_created_at(self):
        high_score = HighScore.objects.create(username='Player', score=100)
        assert high_score.created_at is not None

    def test_multiple_high_scores_same_user(self):
        user = User.objects.create_user(username='pro', password='pass')
        HighScore.objects.create(user=user, username='pro', score=200)
        HighScore.objects.create(user=user, username='pro', score=400)
        HighScore.objects.create(user=user, username='pro', score=300)
        user_scores = HighScore.objects.filter(user=user)
        assert user_scores.count() == 3
        assert user_scores.first().score == 400  # Highest first


@pytest.mark.django_db
class TestModelRelationships:
    """
        Test relationships between models
    """
    def test_user_can_have_multiple_sessions(self):
        user = User.objects.create_user(username='gamer', password='pass')
        for i in range(5):
            GameSession.objects.create(
                user=user,
                score=i * 100,
                moves=i * 50
            )
        assert user.gamesession_set.count() == 5

    def test_user_can_have_multiple_high_scores(self):
        user = User.objects.create_user(username='scorer', password='pass')
        for i in range(3):
            HighScore.objects.create(
                user=user,
                username='scorer',
                score=(i + 1) * 1000
            )
        assert user.highscore_set.count() == 3

    def test_delete_user_deletes_sessions(self):
        user = User.objects.create_user(username='temp', password='pass')
        GameSession.objects.create(user=user, score=100)
        GameSession.objects.create(user=user, score=200)
        assert GameSession.objects.filter(user=user).count() == 2
        user.delete()
        assert GameSession.objects.filter(user=user).count() == 0


@pytest.mark.django_db
class TestQueryOptimization:
    """
        Test database query patterns
    """
    def test_get_top_scores(self):
        # Create various scores
        for i in range(10):
            HighScore.objects.create(
                username=f'Player{i}',
                score=(i + 1) * 100
            )
        # Get top 5 scores
        top_scores = HighScore.objects.all()[:5]
        assert len(top_scores) == 5
        assert top_scores[0].score == 1000  # Highest
        assert top_scores[4].score == 600

    def test_get_user_best_score(self):
        user = User.objects.create_user(username='player', password='pass')
        HighScore.objects.create(user=user, username='player', score=100)
        HighScore.objects.create(user=user, username='player', score=500)
        HighScore.objects.create(user=user, username='player', score=300)
        best_score = HighScore.objects.filter(user=user).first()
        assert best_score.score == 500

    def test_get_recent_sessions(self):
        user = User.objects.create_user(username='player', password='pass')
        for i in range(5):
            GameSession.objects.create(
                user=user,
                score=i * 50
            )
        recent_sessions = GameSession.objects.filter(user=user)[:3]
        assert len(recent_sessions) == 3


@pytest.mark.django_db
class TestDataValidation:
    """
        Test model field validation
    """
    def test_negative_score_allowed(self):
        # In case you want to track penalties
        session = GameSession.objects.create(score=-10)
        assert session.score == -10

    def test_zero_score_allowed(self):
        session = GameSession.objects.create(score=0)
        assert session.score == 0

    def test_large_score_allowed(self):
        session = GameSession.objects.create(score=999999)
        assert session.score == 999999

    def test_empty_username_uses_default(self):
        high_score = HighScore.objects.create(score=100)
        assert high_score.username == 'Anonymous'


@pytest.mark.django_db
class TestModelMethods:
    """
        Test custom model methods if any are added
    """
    def test_game_session_duration_in_minutes(self):
        session = GameSession.objects.create(duration=150)  # seconds
        # If you add a method to convert to minutes
        # minutes = session.duration_in_minutes()
        # assert minutes == 2.5
        pass  # Placeholder for future methods

    def test_high_score_rank(self):
        # Create scores
        HighScore.objects.create(username='P1', score=1000)
        HighScore.objects.create(username='P2', score=800)
        HighScore.objects.create(username='P3', score=600)
        # If you add a method to get rank
        # score = HighScore.objects.get(username='P2')
        # assert score.get_rank() == 2
        pass  # Placeholder for future methods