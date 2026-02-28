#!/usr/bin/env python3
"""
🎯 Bulls & Cows - FastAPI Server
A long-running API for instant telegram game responses.
"""

import random
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = Path("game.db")
MAX_GUESSES = 10

# Pydantic models
class GuessRequest(BaseModel):
    chat_id: str
    guess: str

class ChatRequest(BaseModel):
    chat_id: str

class GameResponse(BaseModel):
    message: str
    status: str
    guesses_left: Optional[int] = None

# Database setup
def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            chat_id TEXT PRIMARY KEY,
            secret TEXT NOT NULL,
            guesses TEXT DEFAULT '[]',
            status TEXT DEFAULT 'playing',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_game(chat_id: str) -> Optional[dict]:
    """Get game by chat_id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "chat_id": row[0],
            "secret": row[1],
            "guesses": eval(row[2]) if row[2] else [],
            "status": row[3],
            "created_at": row[4]
        }
    return None

def save_game(chat_id: str, secret: str, guesses: list, status: str):
    """Save or update game."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO games (chat_id, secret, guesses, status)
        VALUES (?, ?, ?, ?)
    ''', (chat_id, secret, str(guesses), status))
    conn.commit()
    conn.close()

# Game logic
def generate_secret() -> str:
    """Generate a random 4-digit number with unique digits."""
    digits = random.sample(range(10), 4)
    return ''.join(map(str, digits))

def validate_guess(guess: str) -> tuple[bool, str]:
    """Validate a guess."""
    if not guess.isdigit():
        return False, "❌ Please enter digits only (e.g., 1234)"
    if len(guess) != 4:
        return False, f"❌ Must be exactly 4 digits (you entered {len(guess)})"
    if len(set(guess)) != 4:
        return False, "❌ All digits must be unique (no repeats)"
    return True, ""

def calculate_bulls_cows(secret: str, guess: str) -> tuple[int, int]:
    """Calculate bulls and cows."""
    bulls = sum(s == g for s, g in zip(secret, guess))
    cows = len(set(secret) & set(guess)) - bulls
    return bulls, cows

def format_board(game: dict) -> str:
    """Format the game board."""
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

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    init_db()
    print("🎮 Bulls & Cows server started!")
    print("Available at: http://localhost:8765")
    yield
    print("Server shutting down...")

app = FastAPI(title="Bulls & Cows API", lifespan=lifespan)

@app.post("/game/start", response_model=GameResponse)
async def start_game(request: ChatRequest):
    """Start a new game."""
    secret = generate_secret()
    save_game(request.chat_id, secret, [], "playing")
    
    return GameResponse(
        message=(
            "🎮 *NEW GAME STARTED!* 🎮\n\n"
            "I'm thinking of a 4-digit number with unique digits.\n"
            "Try to guess it!\n\n"
            "🎯 *Bull* = correct digit in correct position\n"
            "🐄 *Cow* = correct digit in wrong position\n\n"
            f"You have {MAX_GUESSES} guesses. Good luck!\n\n"
            "Send your first guess (4 digits):"
        ),
        status="playing",
        guesses_left=MAX_GUESSES
    )

@app.post("/game/guess", response_model=GameResponse)
async def make_guess(request: GuessRequest):
    """Make a guess."""
    game = get_game(request.chat_id)
    
    if not game or game['status'] != 'playing':
        return GameResponse(
            message="❌ No active game! Send /startgame to begin.",
            status="none"
        )
    
    # Validate
    is_valid, error = validate_guess(request.guess)
    if not is_valid:
        return GameResponse(message=error, status="playing", guesses_left=MAX_GUESSES - len(game['guesses']))
    
    # Check if already guessed
    if any(g['guess'] == request.guess for g in game['guesses']):
        return GameResponse(
            message=f"⚠️ You already guessed {request.guess}! Try a different number.",
            status="playing",
            guesses_left=MAX_GUESSES - len(game['guesses'])
        )
    
    # Calculate result
    bulls, cows = calculate_bulls_cows(game['secret'], request.guess)
    
    # Record guess
    game['guesses'].append({
        'guess': request.guess,
        'bulls': bulls,
        'cows': cows
    })
    
    # Check win/lose
    if bulls == 4:
        save_game(request.chat_id, game['secret'], game['guesses'], "won")
        return GameResponse(
            message=(
                f"🎉 *YOU WON!* 🎉\n\n"
                f"The secret was: `{game['secret']}`\n"
                f"You guessed it in {len(game['guesses'])} tries!\n\n"
                f"🏆 Well done! Send /startgame to play again."
            ),
            status="won",
            guesses_left=0
        )
    
    if len(game['guesses']) >= MAX_GUESSES:
        save_game(request.chat_id, game['secret'], game['guesses'], "lost")
        return GameResponse(
            message=(
                f"💀 *GAME OVER* 💀\n\n"
                f"You've used all {MAX_GUESSES} guesses.\n"
                f"The secret number was: `{game['secret']}`\n\n"
                f"Better luck next time! Send /startgame to try again."
            ),
            status="lost",
            guesses_left=0
        )
    
    # Still playing
    save_game(request.chat_id, game['secret'], game['guesses'], "playing")
    
    result = f"🎯 Bulls: {bulls}  🐄 Cows: {cows}"
    board = format_board(game)
    
    return GameResponse(
        message=f"{result}\n\n{board}\n\nSend your next guess:",
        status="playing",
        guesses_left=MAX_GUESSES - len(game['guesses'])
    )

@app.get("/game/status/{chat_id}", response_model=GameResponse)
async def get_status(chat_id: str):
    """Get game status."""
    game = get_game(chat_id)
    
    if not game:
        return GameResponse(
            message="🤷 No game found. Send /startgame to play!",
            status="none"
        )
    
    if game['status'] == 'playing':
        return GameResponse(
            message=format_board(game),
            status="playing",
            guesses_left=MAX_GUESSES - len(game['guesses'])
        )
    else:
        return GameResponse(
            message=f"📊 Last game: {game['status'].upper()}\nSecret was: `{game['secret']}`\n\nSend /startgame to play again!",
            status=game['status'],
            guesses_left=0
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
