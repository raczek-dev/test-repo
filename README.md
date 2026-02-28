# 🎮 Bulls & Cows - Telegram Game

A number guessing game (Mastermind-style) for OpenClaw/Telegram integration.

## How to Play

1. **Start a game**: Send `/startgame`
2. **Make guesses**: Send a 4-digit number (e.g., `1234`)
3. **Get feedback**:
   - 🎯 **Bull** = correct digit in correct position
   - 🐄 **Cow** = correct digit in wrong position
4. **Win**: Guess the secret number in 10 tries or less!

## Commands

| Command | Description |
|---------|-------------|
| `/startgame` | Start a new game |
| `/hint` | Get a random hint |
| `/status` | Show current game board |
| `/help` | Show help message |

## OpenClaw Integration

### Quick Start

Add this to your OpenClaw session to enable game commands:

```python
# In your OpenClaw session or hook
import subprocess
import json

def play_bulls_cows(chat_id: str, message: str) -> str:
    \"\"\"Process a game message.\"\"\"
    result = subprocess.run(
        ['python3', 'telegram-game/main.py', '--chat-id', chat_id, '--message', message],
        capture_output=True,
        text=True,
        cwd='/home/lukasz/.openclaw/workspace'
    )
    return result.stdout.strip()
```

### Using Exec Tool

From OpenClaw, you can run:

```bash
# Start a game
exec command:"cd telegram-game && python3 -c 'from main import process_message; print(process_message(\"73182477\", \"/startgame\"))'"

# Make a guess
exec command:"cd telegram-game && python3 -c 'from main import process_message; print(process_message(\"73182477\", \"1234\"))'"
```

### Recommended: Game Router Hook

Create a hook to automatically route game commands:

```javascript
// hooks/game-router.js
const { exec } = require('child_process');

module.exports = {
  async onMessage(message, context) {
    const gameCommands = ['/startgame', '/hint', '/status', '/help'];
    const isGuess = /^\d{4}$/.test(message.text);
    
    if (gameCommands.includes(message.text) || isGuess) {
      const result = await new Promise((resolve, reject) => {
        exec(
          `python3 telegram-game/main.py --chat-id ${message.chat.id} --message "${message.text}"`,
          (err, stdout) => err ? reject(err) : resolve(stdout.trim())
        );
      });
      
      return { reply: result };
    }
    
    return null; // Let other handlers process
  }
};
```

## Game Logic

- Secret number: 4 unique digits (0-9)
- Max guesses: 10
- No repeated guesses allowed
- All digits must be unique in your guess

## Files

- `main.py` - Game logic and Telegram integration
- `game-state.json` - Stores active games (auto-created)
- `README.md` - This file

## Local Testing

Run in CLI mode:

```bash
cd telegram-game
python3 main.py --cli
```

## Tips for Players

1. Start with `1234` or `5678` to narrow down digits
2. Use process of elimination
3. Check your guess history with `/status`
4. Use `/hint` if you're stuck (but try to solve it first!)

---

Built for Lukasz & family 🦞
