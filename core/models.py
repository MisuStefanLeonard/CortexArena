from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class UserProfile(AbstractUser):
    # Override the related_name on these permission/group relations so they
    # don't clash with the default auth.User reverse accessors when both
    # models are present in the project (avoids fields.E304 errors).
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='userprofile_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='userprofile_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    xp_total = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    def xp_for_level(self, level):
        """Calculate XP required for a given level (exponential growth)"""
        # Level 1 = 0 XP, Level 2 = 100 XP, Level 3 = 250 XP, etc.
        # Formula: 50 * level^2 - 50 * level
        return 50 * (level ** 2) - (50 * level)

    def check_level_up(self):
        """Check if user should level up and apply levels"""
        leveled_up = False
        while self.xp_total >= self.xp_for_level(self.level + 1):
            self.level += 1
            leveled_up = True
        if leveled_up:
            self.save()
        return leveled_up

    def xp_to_next_level(self):
        """Get remaining XP needed for next level"""
        next_level_xp = self.xp_for_level(self.level + 1)
        return max(0, next_level_xp - self.xp_total)

    def xp_progress_percentage(self):
        """Get progress percentage towards next level"""
        current_level_xp = self.xp_for_level(self.level)
        next_level_xp = self.xp_for_level(self.level + 1)
        level_xp_range = next_level_xp - current_level_xp
        xp_in_level = self.xp_total - current_level_xp
        if level_xp_range <= 0:
            return 100
        return min(100, max(0, (xp_in_level / level_xp_range) * 100))


class GameType(models.Model):
    MEMORY = "MEM"
    ATTENTION = "ATT"
    LOGIC = "LOG"
    REACTION = "REA"
    SHUFFLE = "SHF"

    GAME_CHOICES = [
        (MEMORY, "Memorie"),
        (ATTENTION, "Atenție"),
        (LOGIC, "Logică"),
        (REACTION, "Reacție"),
        (SHUFFLE, "Pahare"),
    ]

    name = models.CharField(max_length=16, choices=GAME_CHOICES, unique=True)

    def __str__(self):
        return dict(self.GAME_CHOICES).get(self.name, self.name)


class Game(models.Model):
    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"

    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, "Easy"),
        (DIFFICULTY_MEDIUM, "Medium"),
        (DIFFICULTY_HARD, "Hard"),
    ]

    name = models.CharField(max_length=128)
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE, related_name="games")
    difficulty = models.CharField(max_length=16, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_EASY)
    config_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_difficulty_display()})"


class Session(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(default=0)
    xp_gained = models.IntegerField(default=0)

    def __str__(self):
        return f"Session {self.id} - {self.user.username}"


class SessionGame(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_games")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="session_entries")
    score = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0.0)
    time_spent_sec = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.game.name} in session {self.session.id}"


class Stats(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="stats")
    memory_avg = models.FloatField(default=0.0)
    reflex_avg = models.FloatField(default=0.0)
    logic_avg = models.FloatField(default=0.0)
    focus_avg = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stats for {self.user.username}"

class WeeklyStats(models.Model):
    """Track weekly performance for each game type and difficulty"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="weekly_stats")
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE, related_name="weekly_stats")
    difficulty = models.CharField(max_length=16, choices=Game.DIFFICULTY_CHOICES, default='easy')
    week_start = models.DateField()  # Monday of the week
    
    # Aggregate stats
    games_played = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    best_score = models.IntegerField(default=0)
    best_accuracy = models.FloatField(default=0.0)
    best_time_sec = models.IntegerField(default=0)
    
    # Last updated
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'game_type', 'difficulty', 'week_start']
        ordering = ['-week_start', 'game_type', 'difficulty']
    
    def __str__(self):
        return f"{self.user.username} - {self.game_type} ({self.difficulty}) - Week {self.week_start}"
