
from django.contrib import admin
from django.urls import path
from core import views  
from core.views import HomePageView
from core.views import PlayMemoryView
from core.views import submit_memory
from core.views import PlayReactionView
from core.views import submit_reaction
from core.views import PlayLogicView
from core.views import submit_logic
from core.views import PlayAttentionView
from core.views import submit_attention
from core.views import PlayCupShuffleView
from core.views import submit_cup_shuffle
from core.views import LoginView, RegisterView, LogoutView, StatsView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('home/', HomePageView.as_view(), name='home'), 
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('play/memory/', PlayMemoryView.as_view(), name='play_memory'),
    path('play/memory/submit/', submit_memory, name='submit_memory'),
    path('play/reaction/', PlayReactionView.as_view(), name='play_reaction'),
    path('play/reaction/submit/', submit_reaction, name='submit_reaction'),
    path('play/logic/', PlayLogicView.as_view(), name='play_logic'),
    path('play/logic/submit/', submit_logic, name='submit_logic'),
    path('play/attention/', PlayAttentionView.as_view(), name='play_attention'),
    path('play/attention/submit/', submit_attention, name='submit_attention'),
    path('play/cups/', PlayCupShuffleView.as_view(), name='play_cups'),
    path('play/cups/submit/', submit_cup_shuffle, name='submit_cup_shuffle'),
    path('begin/', views.begin, name='begin'),
]
