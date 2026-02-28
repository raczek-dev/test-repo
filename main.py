#!/usr/bin/env python3
"""
🎯 Bulls & Cows - Telegram Number Guessing Game
A simple Mastermind-style game for OpenClaw/Telegram integration.
"""

import json
import random
import os
from datetime import datetime
from typing import Tuple, Optional

STATE_FILE = "game-state.json"
MAX_GUESSES = 10

def load_state() -> dict:
    """Load game state from file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state: dict):
    """Save game state to file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def generate_secret() -> str:
    """Generate a random 4-digit number with unique digits."""
    digits = random.sample(range(10), 4)
    return ''.join(map(str, digits))

def validate_guess(guess: str) -> Tuple[bool, str]:
    """Validate a guess. Returns (is_valid, error_message)."""
    if not guess.isdigit():
        return False, "❌ Please enter digits only (e.g., 1234)"
    if len(guess) != 4:
        return False, f"❌ Must be exactly 4 digits (you entered {len(guess)})"
    if len(set(guess)) != 4:
        return False, "❌ All digits must be unique (no repeats)"
    return True, ""

def calculate_bulls_cows(secret: str, guess: str) -> Tuple[int, int]:
    """Calculate bulls (correct position) and cows (wrong position)."""
    bulls = sum(s == g for s, g in zip(secret, guess))
    cows = len(set(secret) & set(guess)) - bulls
    return bulls, cows

def format_bulls_cows(bulls: int, cows: int) -> str:
    """Format bulls and cows with emojis."""
    bull_emoji = "🎯"
    cow_emoji = "🐄"
    return f"{bull_emoji} Bulls: {bulls}  {cow_emoji} Cows: {cows}"

def format_board(game: dict) -> str:
    """Format the game board with history."""
    lines = [
        "🎮 *BULLS & COWS* 🎮",
        f"Guesses left: {MAX_GUESSES - len(game['guesses'])} / {MAX_GUESSES}",
        "",
        "📜 History:",
        "```",
        "Guess  Bulls Cows",
        "─────  ───── ────"
    ]
    
    for g in game['guesses']:
        lines.append(f" {g['guess']}    {g['bulls']}     {g['cows']}")
    
    lines.append("```")
    return "\n".join(lines)

def start_game(chat_id: str) -> str:
    """Start a new game for a chat."""
    state = load_state()
    
    game = {
        "secret": generate_secret(),
        "guesses": [],
        "started_at": datetime.now().isoformat(),
        "status": "playing"
    }
    
    state[chat_id] = game
    save_state(state)
    
    return (
        "🎮 *NEW GAME STARTED!* 🎮\n\n"
        "I'm thinking of a 4-digit number with unique digits.\n"
        "Try to guess it!\n\n"
        "🎯 *Bull* = correct digit in correct position\n"
        "🐄 *Cow* = correct digit in wrong position\n\n"
        f"You have {MAX_GUESSES} guesses. Good luck!\n\n"
        "Send your first guess (4 digits):"
    )

def make_guess(chat_id: str, guess: str) -> str:
    """Process a guess."""
    state = load_state()
    
    if chat_id not in state or state[chat_id].get('status') != 'playing':
        return "❌ No active game! Send /startgame to begin."
    
    game = state[chat_id]
    
    # Validate
    is_valid, error = validate_guess(guess)
    if not is_valid:
        return error
    
    # Check if already guessed
    if any(g['guess'] == guess for g in game['guesses']):
        return f"⚠️ You already guessed {guess}! Try a different number."
    
    # Calculate result
    bulls, cows = calculate_bulls_cows(game['secret'], guess)
    
    # Record guess
    game['guesses'].append({
        'guess': guess,
        'bulls': bulls,
        'cows': cows,
        'at': datetime.now().isoformat()
    })
    
    # Check win/lose
    if bulls == 4:
        game['status'] = 'won'
        save_state(state)
        return (
            f"🎉 *YOU WON!* 🎉\n\n"
            f"The secret was: `{game['secret']}`\n"
            f"You guessed it in {len(game['guesses'])} tries!\n\n"
            f"🏆 Well done! Send /startgame to play again."
        )
    
    if len(game['guesses']) >= MAX_GUESSES:
        game['status'] = 'lost'
        save_state(state)
        return (
            f"💀 *GAME OVER* 💀\n\n"
            f"You've used all {MAX_GUESSES} guesses.\n"
            f"The secret number was: `{game['secret']}`\n\n"
            f"Better luck next time! Send /startgame to try again."
        )
    
    # Still playing
    save_state(state)
    
    result = format_bulls_cows(bulls, cows)
    board = format_board(game)
    
    return f"{result}\n\n{board}\n\nSend your next guess:"

def get_hint(chat_id: str) -> str:
    """Give a hint about the secret number."""
    state = load_state()
    
    if chat_id not in state or state[chat_id].get('status') != 'playing':
        return "❌ No active game! Send /startgame to begin."
    
    game = state[chat_id]
    secret = game['secret']
    
    hints = [
        f"💡 The first digit is {secret[0]}",
        f"💡 One of the digits is {random.choice(secret)}",
        f"💡 The sum of all digits is {sum(int(d) for d in secret)}",
        f"💡 The last digit is {secret[3]}",
    ]
    
    return random.choice(hints)

def get_status(chat_id: str) -> str:
    """Get current game status."""
    state = load_state()
    
    if chat_id not in state:
        return "🤷 No game found. Send /startgame to play!"
    
    game = state[chat_id]
    
    if game['status'] == 'playing':
        return format_board(game)
    else:
        return f"📊 Last game: {game['status'].upper()}\nSecret was: `{game['secret']}`\n\nSend /startgame to play again!"

def process_message(chat_id: str, message: str) -> str:
    """Main entry point for processing Telegram messages."""
    message = message.strip().lower()
    
    if message == '/startgame':
        return start_game(chat_id)
    elif message == '/hint':
        return get_hint(chat_id)
    elif message == '/status':
        return get_status(chat_id)
    elif message == '/help':
        return (
            "🎮 *BULLS & COWS - Help*\n\n"
            "Commands:\n"
            "• /startgame - Start a new game\n"
            "• /hint - Get a hint (if stuck)\n"
            "• /status - Show game status\n"
            "• /help - Show this message\n\n"
            "To play:\n"
            "1. Send /startgame\n"
            "2. Guess the 4-digit secret number\n"
            "3. 🎯 = correct position, 🐄 = correct digit, wrong position\n"
            "4. You have 10 guesses!"
        )
    else:
        # Assume it's a guess attempt
        return make_guess(chat_id, message)

def cli_mode():
    """CLI mode for local testing."""
    print("🎮 Bulls & Cows - CLI Mode")
    print("Type /startgame to begin, /quit to exit\n")
    
    chat_id = "cli_user"
    
    while True:
        try:
            message = input("> ").strip()
            if message == '/quit':
                break
            
            response = process_message(chat_id, message)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nThanks for playing! 👋")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        cli_mode()
    else:
        # Example Telegram integration usage
        print("Bulls & Cows Game - Telegram Integration")
        print("=" * 50)
        print()
        print("Usage from OpenClaw:")
        print('  exec command:"python3 main.py --chat-id 12345 --message 1234"')
        print("\nOr use process_message() directly in your code.")
