# Contributing to Mind Arena

First off, thank you for considering contributing to Mind Arena! It's people like you that make Mind Arena such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python/Django styleguides
* Include appropriate test cases
* Document new code based on the Documentation Styleguide
* End all files with a newline

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Example:
  ```
  Add XP boost for weekend games
  
  - Implement 1.5x multiplier for Friday-Sunday games
  - Update WeeklyStats to track weekend bonuses
  - Add feature flag for future customization
  
  Fixes #123
  ```

### Python/Django Styleguide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use meaningful variable names
* Keep functions small and focused
* Add docstrings to functions and classes
* Use type hints where appropriate
* Example:
  ```python
  def calculate_xp(base: int, difficulty: str, accuracy: float) -> int:
      """
      Calculate XP based on game performance.
      
      Args:
          base: Base XP value for the game
          difficulty: Game difficulty (easy, medium, hard)
          accuracy: Accuracy percentage (0-1)
      
      Returns:
          Calculated XP amount
      """
      multiplier = {'easy': 1.0, 'medium': 1.5, 'hard': 2.0}
      return int(base * multiplier.get(difficulty, 1.0) * accuracy)
  ```

### JavaScript Styleguide

* Use `const` and `let` instead of `var`
* Use arrow functions where appropriate
* Use meaningful variable names
* Add comments for complex logic
* Example:
  ```javascript
  const calculateScore = (correct, total, time) => {
      const accuracy = correct / total;
      const timeBonus = Math.max(0, 100 - time);
      return Math.round((accuracy * 100) + timeBonus);
  };
  ```

### HTML/CSS Styleguide

* Use semantic HTML elements
* Use BEM (Block Element Modifier) naming for CSS classes
* Keep CSS organized and commented
* Use CSS variables for colors and sizes
* Example:
  ```html
  <div class="game-card game-card--memory">
      <h2 class="game-card__title">Memory Game</h2>
      <p class="game-card__description">Match pairs of cards</p>
      <button class="game-card__button">Play</button>
  </div>
  ```

## Development Setup

1. Fork and clone the repository
   ```bash
   git clone https://github.com/yourusername/mind-arena.git
   cd mind-arena
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Create `.env` file with local settings
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:password@localhost/mindarena
   ```

5. Run migrations
   ```bash
   python manage.py migrate
   ```

6. Create superuser
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server
   ```bash
   python manage.py runserver
   ```

## Testing

Before submitting a PR, please run tests:

```bash
python manage.py test
```

## Documentation

* Update README.md if changing functionality
* Add docstrings to new functions
* Update CHANGELOG.md with significant changes
* Include comments for non-obvious code

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good-first-issue` - Good for newcomers
* `help-wanted` - Extra attention is needed
* `wontfix` - This will not be worked on

## Questions?

Feel free to open an issue or contact the maintainers!

---

Thank you for your interest in contributing to Mind Arena! 🎉
