# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-05

### Added

#### Core Features
- 🧠 **4 Cognitive Mini-Games**:
  - Memory matching game with difficulty levels (6, 9, 12 pairs)
  - Reaction time testing (5, 8, 12 trials)
  - Logic puzzle solver (5, 8, 10 puzzles)
  - Attention tracking game (5, 8, 10 rounds)

- 🎮 **Adventure Roadmap System**:
  - 8 interactive locations with unique aesthetics
  - 8 levels per location (64 total levels)
  - Progressive difficulty (Easy → Medium → Hard)
  - Boss levels (7-8) with hard sequences
  - Animated player character movement
  - Progressive location unlocking (8 games = 1 new location)

- 👤 **User Authentication**:
  - User registration with email validation
  - Secure login/logout
  - Custom UserProfile model extending Django's AbstractUser
  - Password hashing with PBKDF2

- 📊 **XP & Level System**:
  - Dynamic XP calculation based on performance
  - Exponential level requirements (50×level² - 50×level)
  - Auto level-up on XP threshold
  - Visual progress bars
  - XP multipliers for difficulty levels

- 📈 **Statistics Tracking**:
  - Per-game session recording
  - Weekly statistics aggregation
  - Best scores and accuracy tracking
  - Personal game history

- 🏠 **User Dashboard**:
  - Profile card with level, XP, and streak info
  - Game hub with quick access
  - Weekly stats overview
  - Recent game sessions

- 📱 **Responsive Design**:
  - Mobile-first approach
  - Desktop, tablet, and phone optimization
  - Smooth animations and transitions

### Technical Implementation

- Django 5.2.7 backend
- PostgreSQL database
- HTML5 Canvas for game rendering
- ES6 JavaScript with Fetch API
- CSS3 with gradients and animations
- Session-based authentication
- CSRF protection for all POST endpoints

### Database Models

- **UserProfile**: Extended user model with XP, level, streaks
- **GameType**: Memory, Reaction, Logic, Attention
- **Game**: Individual game configurations
- **Session**: User game sessions with timestamps
- **SessionGame**: Per-game performance data
- **WeeklyStats**: Aggregated weekly statistics

### Pages & Routes

- `/` - Home dashboard
- `/begin/` - Adventure roadmap
- `/login/` - User authentication
- `/register/` - New user registration
- `/logout/` - User logout
- `/stats/` - Statistics dashboard
- `/play/memory/` - Memory game
- `/play/reaction/` - Reaction game
- `/play/logic/` - Logic game
- `/play/attention/` - Attention game
- `/play/*/submit/` - Game result submission

## [0.9.0] - 2025-12-01

### Added (Beta Features)
- Basic game implementations
- User authentication skeleton
- Database schema definition
- Initial UI/UX design

### Known Issues
- Canvas roadmap needed better organization
- Level tracking not persistent

## Future Roadmap

### [1.1.0] - Leaderboards & Social
- [ ] Global leaderboards
- [ ] Weekly rankings
- [ ] Friend system
- [ ] Challenges against friends
- [ ] Social sharing

### [1.2.0] - Achievements & Rewards
- [ ] Achievement system with badges
- [ ] Daily challenges
- [ ] Bonus XP events
- [ ] Special power-ups
- [ ] Reward shop

### [1.3.0] - Analytics & IQ
- [ ] IQ score calculation
- [ ] Performance analytics
- [ ] Personalized recommendations
- [ ] Brain health metrics
- [ ] Detailed performance reports

### [1.4.0] - Customization
- [ ] User avatars
- [ ] Theme selection
- [ ] Custom game settings
- [ ] Difficulty presets
- [ ] Game preferences

### [2.0.0] - Multiplayer & Advanced Features
- [ ] Real-time multiplayer games
- [ ] Team competitions
- [ ] Global tournaments
- [ ] AI opponents
- [ ] Mobile app

## Removed

### [1.0.0]
- Canvas-based linear roadmap (replaced with grid-based level system)
- Single-game per location (now rotating game types)

## Changed

### [1.0.0]
- Redesigned adventure system from circular roadmap to level-based progression
- Improved XP calculation algorithm
- Enhanced UI/UX with better animations
- Refactored game templates for consistency

## Security

### [1.0.0]
- CSRF protection on all forms
- Password hashing with Django's PBKDF2
- SQL injection prevention via ORM
- XSS protection via template escaping
- Secure session management

## Performance

### [1.0.0]
- Optimized database queries
- Client-side localStorage for level tracking
- Responsive animations at 60 FPS
- Lazy loading of game assets

---

## How to Upgrade

### From 0.9.0 to 1.0.0
1. Pull the latest changes
2. Run migrations: `python manage.py migrate`
3. Clear browser cache for updated styles
4. Existing user data automatically compatible

## Contributors

- **Rares Cristache** - Creator & Lead Developer

## Support

For bug reports and feature requests, please open an issue on GitHub.

---

**Last Updated**: December 5, 2025
