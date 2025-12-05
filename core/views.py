from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
import json
from datetime import timedelta, datetime

# Import models locally inside methods to avoid circular import issues


# Helper function to get week start (Monday)
def get_week_start(dt=None):
    """Get the Monday of the week for a given date"""
    if dt is None:
        dt = timezone.now()
    # Convert to date if datetime
    if hasattr(dt, 'date'):
        dt = dt.date()
    # Get Monday (weekday 0)
    days_since_monday = dt.weekday()
    monday = dt - timedelta(days=days_since_monday)
    return monday


# Helper function to update weekly stats
def update_weekly_stats(user, game_type_name, difficulty, xp, score, accuracy, time_spent_sec):
    """Update weekly statistics for a user's game performance"""
    from .models import WeeklyStats, GameType
    
    week_start = get_week_start()
    
    try:
        game_type = GameType.objects.get(name=game_type_name)
        
        # Get or create weekly stats
        weekly_stat, created = WeeklyStats.objects.get_or_create(
            user=user,
            game_type=game_type,
            difficulty=difficulty,
            week_start=week_start,
            defaults={
                'games_played': 0,
                'total_xp': 0,
                'best_score': 0,
                'best_accuracy': 0.0,
                'best_time_sec': 0
            }
        )
        
        # Update stats
        weekly_stat.games_played += 1
        weekly_stat.total_xp += xp
        
        # Update bests
        if score > weekly_stat.best_score:
            weekly_stat.best_score = score
        if accuracy > weekly_stat.best_accuracy:
            weekly_stat.best_accuracy = accuracy
        if time_spent_sec > 0 and (weekly_stat.best_time_sec == 0 or time_spent_sec < weekly_stat.best_time_sec):
            weekly_stat.best_time_sec = time_spent_sec
        
        weekly_stat.save()
    except Exception:
        pass  # Silently fail if stats update fails


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Recommended games (limit to a small number) — import here to avoid circular imports
        from .models import Game, WeeklyStats
        ctx['recommended_games'] = Game.objects.select_related('game_type').all()[:8]

        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            ctx['user_summary'] = {
                'username': getattr(user, 'username', 'Invitat'),
                'level': getattr(user, 'level', 1),
                'xp_total': getattr(user, 'xp_total', 0),
                'xp_to_next': user.xp_to_next_level(),
                'xp_progress': user.xp_progress_percentage(),
                'streak_days': getattr(user, 'streak_days', 0),
            }
            
            # Get this week's stats
            week_start = get_week_start()
            weekly_stats = WeeklyStats.objects.filter(
                user=user,
                week_start=week_start
            ).select_related('game_type')
            
            ctx['weekly_stats'] = weekly_stats
            ctx['total_games_this_week'] = sum(ws.games_played for ws in weekly_stats)
            ctx['total_xp_this_week'] = sum(ws.total_xp for ws in weekly_stats)
        else:
            ctx['user_summary'] = {
                'username': 'Invitat',
                'level': 1,
                'xp_total': 0,
                'streak_days': 0,
            }

        ctx['now'] = timezone.now()
        return ctx


@method_decorator(login_required, name='dispatch')
class PlayMemoryView(TemplateView):
    """Simple memory matching game view.

    Query params:
    - difficulty: 'easy'|'medium'|'hard' (default: 'easy')

    Context provided:
    - pairs: number of pairs to generate
    - difficulty: selected difficulty
    - now: timestamp
    """
    template_name = 'memory_game.html'

    DIFFICULTY_MAP = {
        'easy': 6,    # 12 cards
        'medium': 9,  # 18 cards
        'hard': 12,   # 24 cards
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        difficulty = self.request.GET.get('difficulty', 'easy')
        pairs = self.DIFFICULTY_MAP.get(difficulty, 6)
        ctx['pairs'] = pairs
        ctx['difficulty'] = difficulty
        # user summary for template (safe for anonymous)
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            ctx['user_summary'] = {
                'username': getattr(user, 'username', 'Invitat'),
                'level': getattr(user, 'level', 1),
                'xp_total': getattr(user, 'xp_total', 0),
                'streak_days': getattr(user, 'streak_days', 0),
            }
        else:
            ctx['user_summary'] = {
                'username': 'Invitat',
                'level': 1,
                'xp_total': 0,
                'streak_days': 0,
            }
        ctx['now'] = timezone.now()
        return ctx


@require_POST
def submit_memory(request):
    """Accepts JSON POST with: pairs, moves, time_spent_sec, difficulty.

    Calculates XP based on difficulty and performance, updates authenticated user's xp_total
    and creates a Session record when possible. Returns JSON: {'xp': int}
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    pairs = int(payload.get('pairs', 0))
    moves = int(payload.get('moves', 0))
    time_spent = int(payload.get('time_spent_sec', 0))
    difficulty = payload.get('difficulty', 'easy')

    # compute xp: base on pairs, efficiency (fewer moves), and time (faster wins more)
    base = max(5, pairs * 10)
    efficiency = (pairs * 2) / max(1, moves) if moves > 0 else 1.0
    ideal_time = max(1, pairs * 5)  # ideal seconds per number of pairs
    time_eff = ideal_time / max(1, time_spent)
    # blend efficiency and time efficiency, clamp between 0.5 and 3.0
    blended = (efficiency + time_eff) / 2.0
    blended = max(0.5, min(blended, 3.0))
    difficulty_mul = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}.get(difficulty, 1.0)
    xp = int(base * difficulty_mul * blended)
    xp = max(1, xp)

    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        # update user xp
        try:
            user.xp_total = getattr(user, 'xp_total', 0) + xp
            user.save(update_fields=['xp_total'])
            
            # Check for level up
            user.check_level_up()
            
            # Update weekly stats
            score = max(0, pairs * 100 - moves * 5 - time_spent)
            accuracy = 1.0  # Memory game always 100% accurate on completion
            update_weekly_stats(user, 'MEM', difficulty, xp, score, accuracy, time_spent)
        except Exception:
            # Fall back silently but continue to return xp
            pass

        # create a Session and SessionGame record (link to a Game if possible)
        try:
            from .models import Session, SessionGame, Game, GameType

            # ensure a GameType for memory exists
            gt, _ = GameType.objects.get_or_create(name=GameType.MEMORY)
            # ensure a Game entry exists for the memory game
            game, _ = Game.objects.get_or_create(name='Memorie', game_type=gt, defaults={'difficulty': 'easy', 'config_data': {}})

            now = timezone.now()
            start = now - timedelta(seconds=time_spent)
            # simple scoring heuristic
            score = max(0, pairs * 100 - moves * 5 - time_spent)
            session = Session.objects.create(user=user, start_time=start, end_time=now, total_score=score, xp_gained=xp)
            # record the per-game details
            SessionGame.objects.create(session=session, game=game, score=score, accuracy=1.0, time_spent_sec=time_spent)
        except Exception:
            pass

    return JsonResponse({'xp': xp})


def home(request):
    return render(request, 'home.html')


@method_decorator(login_required, name='dispatch')
class PlayReactionView(TemplateView):
    """Reaction time test game view.

    Query params:
    - difficulty: 'easy'|'medium'|'hard' (default: 'easy')

    Context provided:
    - trials: number of reaction trials
    - difficulty: selected difficulty
    - user_summary: user info
    - now: timestamp
    """
    template_name = 'reaction_game.html'

    DIFFICULTY_MAP = {
        'easy': 5,    # 5 trials
        'medium': 8,  # 8 trials
        'hard': 12,   # 12 trials
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        difficulty = self.request.GET.get('difficulty', 'easy')
        trials = self.DIFFICULTY_MAP.get(difficulty, 5)
        ctx['trials'] = trials
        ctx['difficulty'] = difficulty
        # user summary for template (safe for anonymous)
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            ctx['user_summary'] = {
                'username': getattr(user, 'username', 'Invitat'),
                'level': getattr(user, 'level', 1),
                'xp_total': getattr(user, 'xp_total', 0),
                'streak_days': getattr(user, 'streak_days', 0),
            }
        else:
            ctx['user_summary'] = {
                'username': 'Invitat',
                'level': 1,
                'xp_total': 0,
                'streak_days': 0,
            }
        ctx['now'] = timezone.now()
        return ctx


@require_POST
def submit_reaction(request):
    """Accepts JSON POST with: trials, reaction_times (array of ms), difficulty.

    Calculates XP based on difficulty and average reaction time, updates user's xp_total
    and creates Session/SessionGame with reaction times stored in config_data for later analysis.
    Returns JSON: {'xp': int}
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    trials = int(payload.get('trials', 0))
    reaction_times = payload.get('reaction_times', [])  # array of ms
    difficulty = payload.get('difficulty', 'easy')
    time_spent = int(payload.get('time_spent_sec', 0))

    # compute avg reaction time
    if reaction_times:
        avg_rt = sum(reaction_times) / len(reaction_times)
    else:
        avg_rt = 9999

    # compute xp: faster = more xp; base on trials and difficulty
    base = max(10, trials * 8)
    # ideal average reaction time: 300ms; compute speed multiplier
    ideal_rt = 300
    speed_mult = ideal_rt / max(1, avg_rt) if avg_rt > 0 else 0.1
    speed_mult = max(0.3, min(speed_mult, 3.0))  # clamp
    difficulty_mul = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}.get(difficulty, 1.0)
    xp = int(base * speed_mult * difficulty_mul)
    xp = max(1, xp)

    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        # update user xp
        try:
            user.xp_total = getattr(user, 'xp_total', 0) + xp
            user.save(update_fields=['xp_total'])
            
            # Check for level up
            user.check_level_up()
            
            # Update weekly stats
            score = int(10000 / max(1, avg_rt)) if avg_rt > 0 else 0
            update_weekly_stats(user, 'REA', difficulty, xp, score, speed_mult, int(avg_rt))
        except Exception:
            pass

        # create Session and SessionGame with reaction_times stored for IQ/stats later
        try:
            from .models import Session, SessionGame, Game, GameType

            # ensure GameType for reaction exists
            gt, _ = GameType.objects.get_or_create(name=GameType.REACTION)
            # ensure Game entry for reaction test
            game, _ = Game.objects.get_or_create(name='Reacție', game_type=gt, defaults={'difficulty': 'easy', 'config_data': {}})

            now = timezone.now()
            start = now - timedelta(seconds=time_spent)
            # score heuristic: inverse of avg reaction time scaled
            score = int(10000 / max(1, avg_rt)) if avg_rt > 0 else 0
            session = Session.objects.create(user=user, start_time=start, end_time=now, total_score=score, xp_gained=xp)
            # store reaction_times in SessionGame.config_data (JSON field in Game model can hold it, or we use a custom field)
            # For now store in Game.config_data or SessionGame — let's store avg in time_spent_sec and detailed times in a custom way
            # Since SessionGame has time_spent_sec, accuracy — we'll put avg_rt in time_spent_sec (in ms) and store full times in session notes if needed
            # Alternatively: store reaction_times as JSON in SessionGame (we'll need to add a field or use existing ones creatively)
            # Let's use accuracy to store avg_rt normalized, and store full array in a separate model later if needed.
            # For now: time_spent_sec = avg_rt in ms (int), accuracy = speed_mult
            SessionGame.objects.create(session=session, game=game, score=score, accuracy=speed_mult, time_spent_sec=int(avg_rt))
        except Exception:
            pass

    return JsonResponse({'xp': xp, 'avg_reaction_time': int(avg_rt)})


@method_decorator(login_required, name='dispatch')
class PlayLogicView(TemplateView):
    """Logic puzzle game view - sequence pattern solving.

    Query params:
    - difficulty: 'easy'|'medium'|'hard' (default: 'easy')

    Context provided:
    - puzzles_count: number of puzzles
    - difficulty: selected difficulty
    - user_summary: user info
    - now: timestamp
    """
    template_name = 'logic_game.html'

    DIFFICULTY_MAP = {
        'easy': 5,     # 5 puzzles
        'medium': 8,   # 8 puzzles
        'hard': 10,    # 10 puzzles
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        difficulty = self.request.GET.get('difficulty', 'easy')
        puzzles_count = self.DIFFICULTY_MAP.get(difficulty, 5)
        ctx['puzzles_count'] = puzzles_count
        ctx['difficulty'] = difficulty
        # user summary for template (safe for anonymous)
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            ctx['user_summary'] = {
                'username': getattr(user, 'username', 'Invitat'),
                'level': getattr(user, 'level', 1),
                'xp_total': getattr(user, 'xp_total', 0),
                'streak_days': getattr(user, 'streak_days', 0),
            }
        else:
            ctx['user_summary'] = {
                'username': 'Invitat',
                'level': 1,
                'xp_total': 0,
                'streak_days': 0,
            }
        ctx['now'] = timezone.now()
        return ctx


@require_POST
def submit_logic(request):
    """Accepts JSON POST with: puzzles_count, correct_answers, total_puzzles, time_spent_sec, difficulty.

    Calculates XP based on difficulty, accuracy, and speed.
    Returns JSON: {'xp': int}
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    total_puzzles = int(payload.get('total_puzzles', 0))
    correct_answers = int(payload.get('correct_answers', 0))
    time_spent = int(payload.get('time_spent_sec', 0))
    difficulty = payload.get('difficulty', 'easy')

    # compute accuracy
    accuracy = correct_answers / max(1, total_puzzles) if total_puzzles > 0 else 0

    # compute xp: base on puzzles, accuracy, and speed
    base = max(15, total_puzzles * 12)
    accuracy_mult = accuracy  # 0.0 to 1.0
    # ideal time per puzzle: 15s for easy, 20s for medium, 25s for hard
    ideal_time_per_puzzle = {'easy': 15, 'medium': 20, 'hard': 25}.get(difficulty, 15)
    ideal_total = ideal_time_per_puzzle * total_puzzles
    time_eff = ideal_total / max(1, time_spent) if time_spent > 0 else 0.5
    time_eff = max(0.3, min(time_eff, 2.0))  # clamp
    difficulty_mul = {'easy': 1.0, 'medium': 1.6, 'hard': 2.2}.get(difficulty, 1.0)
    xp = int(base * accuracy_mult * time_eff * difficulty_mul)
    xp = max(1, xp)

    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        # update user xp
        try:
            user.xp_total = getattr(user, 'xp_total', 0) + xp
            user.save(update_fields=['xp_total'])
            
            # Check for level up
            user.check_level_up()
            
            # Update weekly stats
            score = int(correct_answers * 100 / max(1, total_puzzles))
            update_weekly_stats(user, 'LOG', difficulty, xp, score, accuracy, time_spent)
        except Exception:
            pass

        # create Session and SessionGame
        try:
            from .models import Session, SessionGame, Game, GameType

            # ensure GameType for logic exists
            gt, _ = GameType.objects.get_or_create(name=GameType.LOGIC)
            # ensure Game entry for logic puzzles
            game, _ = Game.objects.get_or_create(name='Logică', game_type=gt, defaults={'difficulty': 'easy', 'config_data': {}})

            now = timezone.now()
            start = now - timedelta(seconds=time_spent)
            score = int(correct_answers * 100 / max(1, total_puzzles))
            session = Session.objects.create(user=user, start_time=start, end_time=now, total_score=score, xp_gained=xp)
            SessionGame.objects.create(session=session, game=game, score=score, accuracy=accuracy, time_spent_sec=time_spent)
        except Exception:
            pass

    return JsonResponse({'xp': xp, 'accuracy': round(accuracy * 100, 1)})


@method_decorator(login_required, name='dispatch')
class PlayAttentionView(TemplateView):
    """Attention/focus game view - track moving targets among distractors.

    Query params:
    - difficulty: 'easy'|'medium'|'hard' (default: 'easy')

    Context provided:
    - rounds: number of rounds
    - difficulty: selected difficulty
    - user_summary: user info
    - now: timestamp
    """
    template_name = 'attention_game.html'

    DIFFICULTY_MAP = {
        'easy': 5,     # 5 rounds
        'medium': 8,   # 8 rounds
        'hard': 10,    # 10 rounds
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        difficulty = self.request.GET.get('difficulty', 'easy')
        rounds = self.DIFFICULTY_MAP.get(difficulty, 5)
        ctx['rounds'] = rounds
        ctx['difficulty'] = difficulty
        # user summary for template (safe for anonymous)
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            ctx['user_summary'] = {
                'username': getattr(user, 'username', 'Invitat'),
                'level': getattr(user, 'level', 1),
                'xp_total': getattr(user, 'xp_total', 0),
                'streak_days': getattr(user, 'streak_days', 0),
            }
        else:
            ctx['user_summary'] = {
                'username': 'Invitat',
                'level': 1,
                'xp_total': 0,
                'streak_days': 0,
            }
        ctx['now'] = timezone.now()
        return ctx


@require_POST
def submit_attention(request):
    """Accepts JSON POST with: rounds, correct_clicks, total_rounds, time_spent_sec, difficulty.

    Calculates XP based on difficulty, accuracy, and speed.
    Returns JSON: {'xp': int}
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    total_rounds = int(payload.get('total_rounds', 0))
    correct_clicks = int(payload.get('correct_clicks', 0))
    time_spent = int(payload.get('time_spent_sec', 0))
    difficulty = payload.get('difficulty', 'easy')

    # compute accuracy
    accuracy = correct_clicks / max(1, total_rounds) if total_rounds > 0 else 0

    # compute xp: base on rounds, accuracy, and focus (speed bonus)
    base = max(12, total_rounds * 10)
    accuracy_mult = accuracy  # 0.0 to 1.0
    # ideal time per round: 5s for easy, 4s for medium, 3s for hard
    ideal_time_per_round = {'easy': 5, 'medium': 4, 'hard': 3}.get(difficulty, 5)
    ideal_total = ideal_time_per_round * total_rounds
    time_eff = ideal_total / max(1, time_spent) if time_spent > 0 else 0.5
    time_eff = max(0.4, min(time_eff, 2.5))  # clamp
    difficulty_mul = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}.get(difficulty, 1.0)
    xp = int(base * accuracy_mult * time_eff * difficulty_mul)
    xp = max(1, xp)

    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        # update user xp
        try:
            user.xp_total = getattr(user, 'xp_total', 0) + xp
            user.save(update_fields=['xp_total'])
            
            # Check for level up
            user.check_level_up()
            
            # Update weekly stats
            score = int(correct_clicks * 100 / max(1, total_rounds))
            update_weekly_stats(user, 'ATT', difficulty, xp, score, accuracy, time_spent)
        except Exception:
            pass

        # create Session and SessionGame
        try:
            from .models import Session, SessionGame, Game, GameType

            # ensure GameType for attention exists
            gt, _ = GameType.objects.get_or_create(name=GameType.ATTENTION)
            # ensure Game entry for attention test
            game, _ = Game.objects.get_or_create(name='Atenție', game_type=gt, defaults={'difficulty': 'easy', 'config_data': {}})

            now = timezone.now()
            start = now - timedelta(seconds=time_spent)
            score = int(correct_clicks * 100 / max(1, total_rounds))
            session = Session.objects.create(user=user, start_time=start, end_time=now, total_score=score, xp_gained=xp)
            SessionGame.objects.create(session=session, game=game, score=score, accuracy=accuracy, time_spent_sec=time_spent)
        except Exception:
            pass

    return JsonResponse({'xp': xp, 'accuracy': round(accuracy * 100, 1)})


# Authentication Views

class LoginView(View):
    """Handle user login"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            return render(request, 'login.html', {'error': 'Te rugăm să completezi toate câmpurile.'})
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Username sau parolă incorectă.'})


class RegisterView(View):
    """Handle user registration"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'register.html')
    
    def post(self, request):
        from .models import UserProfile
        
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Validation
        if not all([username, email, password1, password2]):
            return render(request, 'register.html', {'error': 'Te rugăm să completezi toate câmpurile.'})
        
        if password1 != password2:
            return render(request, 'register.html', {'error': 'Parolele nu se potrivesc.'})
        
        if len(password1) < 6:
            return render(request, 'register.html', {'error': 'Parola trebuie să aibă minim 6 caractere.'})
        
        if UserProfile.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username-ul este deja folosit.'})
        
        if UserProfile.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email-ul este deja înregistrat.'})
        
        # Create user (password will be automatically hashed by create_user)
        try:
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            user.xp_total = 0
            user.level = 1
            user.streak_days = 0
            user.save()
            
            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Cont creat cu succes!')
            return redirect('home')
        except Exception as e:
            return render(request, 'register.html', {'error': f'Eroare la creare cont: {str(e)}'})


class LogoutView(View):
    """Handle user logout"""
    
    def get(self, request):
        logout(request)
        messages.info(request, 'Ai fost deconectat.')
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class StatsView(TemplateView):
    """Display user statistics and performance data"""
    template_name = 'stats.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from .models import Session, WeeklyStats
        
        user = self.request.user
        week_start = get_week_start()
        
        # Get weekly stats for current week
        ctx['weekly_stats'] = WeeklyStats.objects.filter(
            user=user,
            week_start=week_start
        ).select_related('game_type').order_by('game_type', '-total_xp')
        
        # Get total sessions
        ctx['total_sessions'] = Session.objects.filter(user=user).count()
        
        # Get recent sessions (last 10)
        ctx['recent_sessions'] = Session.objects.filter(
            user=user
        ).order_by('-start_time')[:10]
        
        ctx['week_start'] = week_start
        
        return ctx



def begin(request):
    from .models import Session
    
    user = request.user if request.user.is_authenticated else None
    total_games = 0
    
    if user:
        total_games = Session.objects.filter(user=user).count()
    
    return render(request, 'begin.html', {
        'user': user,
        'total_games': total_games
    })
