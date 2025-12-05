# Mind Arena API Documentation

Complete API reference for Mind Arena game endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints except authentication endpoints require login. Authentication is session-based using Django's built-in authentication system.

### Login

```http
POST /login/
Content-Type: application/x-www-form-urlencoded

username=testuser&password=testpassword
```

### Register

```http
POST /register/
Content-Type: application/x-www-form-urlencoded

username=newuser&email=user@example.com&password=securepass
```

### Logout

```http
GET /logout/
```

## Game Endpoints

### Memory Game

#### Get Game Page

```http
GET /play/memory/?difficulty=easy
```

**Query Parameters:**
- `difficulty` (required): `easy` | `medium` | `hard`
- `loc` (optional): Location index (0-7)
- `level` (optional): Level number (1-8)

**Response:** HTML page with game

#### Submit Results

```http
POST /play/memory/submit/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "pairs": 6,
  "moves": 12,
  "time_spent_sec": 45,
  "difficulty": "easy"
}
```

**Response:**
```json
{
  "xp": 150
}
```

**Parameters:**
- `pairs` (required): Number of pairs in game (6, 9, or 12)
- `moves` (required): Number of moves made
- `time_spent_sec` (required): Game duration in seconds
- `difficulty` (required): Game difficulty level

---

### Reaction Game

#### Get Game Page

```http
GET /play/reaction/?difficulty=easy
```

#### Submit Results

```http
POST /play/reaction/submit/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "trials": 5,
  "reaction_times": [250, 320, 280, 290, 310],
  "time_spent_sec": 30,
  "difficulty": "easy"
}
```

**Response:**
```json
{
  "xp": 175,
  "avg_reaction_time": 290
}
```

**Parameters:**
- `trials` (required): Number of trials
- `reaction_times` (required): Array of reaction times in milliseconds
- `time_spent_sec` (required): Total game time
- `difficulty` (required): Game difficulty

---

### Logic Game

#### Get Game Page

```http
GET /play/logic/?difficulty=easy
```

#### Submit Results

```http
POST /play/logic/submit/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "total_puzzles": 5,
  "correct_answers": 4,
  "time_spent_sec": 120,
  "difficulty": "easy"
}
```

**Response:**
```json
{
  "xp": 165,
  "accuracy": 80
}
```

**Parameters:**
- `total_puzzles` (required): Total number of puzzles
- `correct_answers` (required): Number of correct answers
- `time_spent_sec` (required): Game duration
- `difficulty` (required): Game difficulty

---

### Attention Game

#### Get Game Page

```http
GET /play/attention/?difficulty=easy
```

#### Submit Results

```http
POST /play/attention/submit/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "total_rounds": 5,
  "correct_clicks": 5,
  "time_spent_sec": 60,
  "difficulty": "easy"
}
```

**Response:**
```json
{
  "xp": 155,
  "accuracy": 100
}
```

**Parameters:**
- `total_rounds` (required): Total number of rounds
- `correct_clicks` (required): Number of correct clicks
- `time_spent_sec` (required): Game duration
- `difficulty` (required): Game difficulty

---

## User Pages

### Home Page

```http
GET /
```

Returns home page with:
- User profile information
- Available games
- Weekly statistics

### Adventure Page

```http
GET /begin/
```

Returns adventure roadmap with:
- 8 locations
- 64 levels (8 per location)
- Completion tracking

### Statistics Page

```http
GET /stats/
```

Returns user statistics including:
- Level and XP
- Session history
- Weekly performance

---

## Data Models

### User Profile

```json
{
  "id": 1,
  "username": "player1",
  "email": "player@example.com",
  "level": 5,
  "xp_total": 2500,
  "streak_days": 7,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Game Session

```json
{
  "id": 1,
  "user_id": 1,
  "game_type": "MEMORY",
  "difficulty": "easy",
  "start_time": "2025-01-15T10:30:00Z",
  "end_time": "2025-01-15T10:31:45Z",
  "total_score": 450,
  "xp_gained": 150,
  "accuracy": 0.95,
  "time_spent_sec": 105
}
```

### Weekly Statistics

```json
{
  "id": 1,
  "user_id": 1,
  "game_type": "MEMORY",
  "difficulty": "easy",
  "week_start": "2025-01-13",
  "games_played": 5,
  "total_xp": 750,
  "best_score": 500,
  "best_accuracy": 0.98,
  "best_time_sec": 85
}
```

---

## XP Calculation

### Formula

```
XP = base_xp × difficulty_multiplier × performance_modifier
```

### Base XP by Game Type

| Game | Easy | Medium | Hard |
|------|------|--------|------|
| Memory | 60 | 90 | 120 |
| Reaction | 250 | 375 | 500 |
| Logic | 50 | 75 | 100 |
| Attention | 55 | 82.5 | 110 |

### Difficulty Multiplier

| Difficulty | Multiplier |
|------------|-----------|
| Easy | 1.0 |
| Medium | 1.5 |
| Hard | 2.0 |

### Performance Modifiers

- **Accuracy**: (correct_answers / total) × 1.0
- **Speed**: Varies by game (faster = higher)
- **Efficiency**: (perfect_performance / actual) × 0.5 to 2.0

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid parameters",
  "details": "Missing required parameter: difficulty"
}
```

### 401 Unauthorized

```json
{
  "error": "Authentication required",
  "redirect_url": "/login/"
}
```

### 403 Forbidden

```json
{
  "error": "Permission denied"
}
```

### 404 Not Found

```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "details": "An unexpected error occurred"
}
```

---

## Rate Limiting

Currently no rate limiting. Consider implementing for production:

```
POST /play/*/submit/: 10 requests per minute per user
GET /stats/: 30 requests per minute per user
```

---

## CORS Headers

Currently restricted to same-origin. For API access:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

---

## Pagination

List endpoints support pagination:

```http
GET /stats/?page=1&limit=10
```

Parameters:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20)

---

## Filtering

Filter results by query parameters:

```http
GET /stats/?game_type=MEMORY&difficulty=easy
```

Available filters:
- `game_type`: Game type filter
- `difficulty`: Difficulty level
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)

---

## Sorting

Sort results:

```http
GET /stats/?sort=-created_at
```

Format: `[+/-]field_name`
- Prefix `-` for descending
- Prefix `+` or no prefix for ascending

---

## Examples

### Example 1: Complete Memory Game

```javascript
// 1. Start game
fetch('/play/memory/?difficulty=easy&loc=0&level=1')

// 2. Submit result
const result = await fetch('/play/memory/submit/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    pairs: 6,
    moves: 12,
    time_spent_sec: 45,
    difficulty: 'easy'
  })
});

const data = await result.json();
console.log('XP earned:', data.xp);
```

### Example 2: Get Statistics

```javascript
fetch('/stats/')
  .then(r => r.text())
  .then(html => {
    // Parse HTML for statistics
    console.log(html);
  });
```

---

## WebSocket Support

Currently not implemented. Planned for real-time features:
- Live multiplayer games
- Real-time leaderboards
- Chat functionality

---

## Versioning

API version can be specified via header:

```http
Accept-Version: 1.0
```

Current version: `1.0`

---

## Changelog

### Version 1.0 (Current)
- Initial release
- Game submission endpoints
- User authentication
- Statistics tracking

### Version 2.0 (Planned)
- Leaderboards API
- Multiplayer endpoints
- WebSocket support
- Advanced filtering

---

## Testing API

### Using cURL

```bash
# Get home page
curl http://localhost:8000/

# Submit memory game result
curl -X POST http://localhost:8000/play/memory/submit/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{"pairs": 6, "moves": 12, "time_spent_sec": 45, "difficulty": "easy"}'
```

### Using Postman

1. Import collection from `postman-collection.json`
2. Set environment variables
3. Run requests

### Using Python

```python
import requests

session = requests.Session()

# Login
response = session.post('http://localhost:8000/login/', data={
    'username': 'testuser',
    'password': 'testpass'
})

# Submit game
response = session.post('http://localhost:8000/play/memory/submit/', json={
    'pairs': 6,
    'moves': 12,
    'time_spent_sec': 45,
    'difficulty': 'easy'
})

print(response.json())
```

---

For more information, see [README.md](README.md) and [SETUP.md](SETUP.md)

**Last Updated**: December 2025
