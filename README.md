# 🧠 Mind Arena - Brain Training Platform

A gamified brain training platform built with Django where users can play cognitive mini-games, track progress, and progress through an interactive adventure roadmap.

## 🎮 Features

### Core Gameplay
- **4 Cognitive Mini-Games**:
  - 🧠 **Memory**: Match pairs of cards with increasing difficulty
  - ⚡ **Reaction**: Test your reaction time with visual targets
  - 🧩 **Logic**: Solve pattern recognition puzzles
  - 👁️ **Attention**: Track moving targets among distractors

- **Progressive Difficulty**: Easy → Medium → Hard with adaptive game parameters
- **Dynamic XP System**: Earn XP based on performance (accuracy, speed, efficiency)
- **Level-Up Mechanics**: Exponential XP requirements (50×level² - 50×level)
- **Session Tracking**: All games recorded with scores, accuracy, and time metrics

### Adventure System
- **8 Interactive Locations**: Poiană, Pădure, Munte Lava, Mormânt, Fortăreață, Vulcan, Piață Nebunilor, Castel Negru
- **8 Levels Per Location**: Progressive difficulty levels with rotating game types
- **Boss Levels (7-8)**: Hard difficulty sequence of all 4 games
- **Progressive Unlocking**: Each 8 games completed unlocks next location
- **Animated Player**: Character movement between completed levels

### User Management
- **Custom Authentication**: Register, Login, Logout
- **User Profiles**: Extended with custom XP, level, and streak tracking
- **Weekly Statistics**: Game performance tracked per game type, difficulty, and week
- **Dashboard**: View overall stats, recent sessions, and weekly performance

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Authentication**: Django's built-in auth + custom UserProfile model
- **Storage**: Session-based game data with persistent weekly stats

## 📋 Requirements

```
Python 3.13+
Django 5.2.7
PostgreSQL
```

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/mind-arena.git
cd mind-arena
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database
Create a PostgreSQL database and update `arena/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to start playing!

## 📁 Project Structure

```
arena/
├── core/
│   ├── models.py              # Database models (UserProfile, Game, Session, etc.)
│   ├── views.py               # Game views, authentication, stats
│   ├── admin.py               # Django admin configuration
│   ├── urls.py                # URL routing
│   ├── migrations/            # Database migrations
│   └── templates/
│       ├── begin.html         # Adventure roadmap with 8 locations
│       ├── home.html          # Main dashboard with profile & game hub
│       ├── memory_game.html   # Memory matching game
│       ├── reaction_game.html # Reaction time test
│       ├── logic_game.html    # Pattern recognition puzzles
│       ├── attention_game.html# Target tracking game
│       ├── stats.html         # User statistics dashboard
│       ├── login.html         # Login form
│       └── register.html      # Registration form
├── arena/
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── db.sqlite3                 # Database (if using SQLite)
└── manage.py                  # Django management script
```

## 🎯 Gameplay Mechanics

### XP Calculation
Games award XP based on:
- **Base XP**: Depends on game type (Memory: pairs×10, Reaction: trials×50, etc.)
- **Difficulty Multiplier**: Easy(1.0) → Medium(1.5) → Hard(2.0)
- **Performance Modifiers**:
  - Accuracy: % of correct answers
  - Speed: Faster completion = higher multiplier
  - Efficiency: Better performance metrics

### Level System
- **Exponential Growth**: XP needed for next level = 50×level² - 50×level
- **Auto Level-Up**: Automatically increases when XP threshold reached
- **Progress Tracking**: XP bar shows progress to next level

### Weekly Statistics
Tracked metrics per game, difficulty, and week:
- Games played
- Total XP earned
- Best score
- Best accuracy
- Best time

## 🔐 Authentication

- Users create accounts with email validation
- Passwords hashed using Django's PBKDF2 algorithm
- Login required for gameplay
- Session-based authentication

## 📊 Database Models

### UserProfile
```python
- username (unique)
- email
- password (hashed)
- xp_total: Total XP accumulated
- level: Current level (auto-calculated)
- streak_days: Daily login streak
- created_at: Account creation date
```

### Game & Session Tracking
```python
GameType: Memory, Reaction, Logic, Attention
Session: User game session with start/end times
SessionGame: Per-game details (score, accuracy, time)
WeeklyStats: Weekly aggregated performance
```

## 🎨 UI/UX Design

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Eye-friendly blue gradient background
- **Smooth Animations**: Transitions, particle effects, level completion animations
- **Intuitive Navigation**: Clear menus and navigation paths

## 🚦 How to Play

1. **Register** at `/register/` - Create your account
2. **Login** at `/login/` - Access your profile
3. **Play Games**:
   - From `/` (home): Click on any game card
   - From `/begin/` (adventure): Click on a level to start
4. **Select Difficulty**: Choose Easy, Medium, or Hard
5. **Complete Challenge**: Finish the game based on type
6. **Earn XP**: Get rewarded based on performance
7. **Level Up**: Automatically increase level when XP threshold reached
8. **Track Progress**: View stats at `/stats/`

## 🗺️ Adventure Roadmap

- **8 Locations**: Each with unique aesthetic and difficulty progression
- **64 Total Levels**: 8 per location (8×8 grid structure)
- **Progressive Unlocking**: Complete 8 games = unlock next location
- **Boss Encounters**: Locations 7-8 have special hard-mode sequences
- **Visual Feedback**: Animated player moves between levels, lock icons on blocked areas

## 🔄 URL Routes

| Route | Purpose |
|-------|---------|
| `/` | Home dashboard |
| `/begin/` | Adventure roadmap |
| `/login/` | User login |
| `/register/` | User registration |
| `/logout/` | User logout |
| `/stats/` | User statistics |
| `/play/memory/` | Memory game |
| `/play/reaction/` | Reaction game |
| `/play/logic/` | Logic game |
| `/play/attention/` | Attention game |
| `/play/*/submit/` | Game result submission (POST) |

## 💾 Data Persistence

- **Game Sessions**: Saved immediately after game completion
- **User Progress**: Levels and XP saved to database
- **Weekly Stats**: Aggregated and saved per week (Monday start)
- **Completed Levels**: Tracked in browser localStorage for UI display

## 🌟 Future Enhancements

- [ ] Leaderboards (global/weekly rankings)
- [ ] Achievement system with badges
- [ ] IQ calculation based on performance metrics
- [ ] Multiplayer challenges
- [ ] Custom avatars and themes
- [ ] Advanced analytics dashboard
- [ ] Daily challenges and bonus XP
- [ ] Power-ups and special abilities
- [ ] Social features (friends, teams)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Rares Cristache**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Django community for excellent framework
- PostgreSQL for reliable database
- HTML5 Canvas for game rendering
- All testers and contributors

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: your.email@example.com

---

**Happy Brain Training! 🧠✨**
