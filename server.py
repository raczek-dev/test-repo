import random
import string
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Bulls and Cows API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory game storage keyed by game_id
games: dict[str, dict] = {}


class GuessRequest(BaseModel):
    guess: str


def generate_secret(length: int = 4) -> str:
    """Generate a secret number with unique digits."""
    digits = list(range(0, 10))
    random.shuffle(digits)
    # First digit should not be 0
    if digits[0] == 0:
        for i in range(1, len(digits)):
            if digits[i] != 0:
                digits[0], digits[i] = digits[i], digits[0]
                break
    return "".join(str(d) for d in digits[:length])


def calculate_bulls_cows(secret: str, guess: str) -> tuple[int, int]:
    """Calculate bulls (correct digit in correct position) and cows (correct digit in wrong position)."""
    bulls = sum(s == g for s, g in zip(secret, guess))
    cows = sum(min(secret.count(d), guess.count(d)) for d in set(guess)) - bulls
    return bulls, cows


def make_game_id() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


@app.post("/api/games")
def new_game():
    game_id = make_game_id()
    secret = generate_secret()
    games[game_id] = {"secret": secret, "guesses": [], "won": False}
    return {"game_id": game_id, "digit_count": len(secret)}


@app.post("/api/games/{game_id}/guess")
def make_guess(game_id: str, req: GuessRequest):
    game = games.get(game_id)
    if not game:
        return {"error": "Game not found"}, 404

    guess = req.guess
    if len(guess) != len(game["secret"]) or not guess.isdigit() or len(set(guess)) != len(guess):
        return {"error": f"Guess must be {len(game['secret'])} unique digits"}

    if game["won"]:
        return {"error": "Game already won"}

    bulls, cows = calculate_bulls_cows(game["secret"], guess)
    entry = {"guess": guess, "bulls": bulls, "cows": cows}
    game["guesses"].append(entry)

    won = bulls == len(game["secret"])
    if won:
        game["won"] = True

    return {
        "guess": guess,
        "bulls": bulls,
        "cows": cows,
        "won": won,
        "attempt": len(game["guesses"]),
    }


@app.get("/api/games/{game_id}")
def get_game(game_id: str):
    game = games.get(game_id)
    if not game:
        return {"error": "Game not found"}, 404
    return {
        "game_id": game_id,
        "guesses": game["guesses"],
        "won": game["won"],
        "digit_count": len(game["secret"]),
    }
