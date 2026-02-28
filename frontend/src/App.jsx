import { useState, useCallback } from "react";
import GameBoard from "./components/GameBoard";
import GuessInput from "./components/GuessInput";
import Header from "./components/Header";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [gameId, setGameId] = useState(null);
  const [digitCount, setDigitCount] = useState(4);
  const [guesses, setGuesses] = useState([]);
  const [won, setWon] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const startNewGame = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/games`, { method: "POST" });
      const data = await res.json();
      setGameId(data.game_id);
      setDigitCount(data.digit_count);
      setGuesses([]);
      setWon(false);
    } catch {
      setError("Could not connect to server");
    } finally {
      setLoading(false);
    }
  }, []);

  const submitGuess = useCallback(
    async (guess) => {
      if (!gameId) return;
      setError("");
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/games/${gameId}/guess`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ guess }),
        });
        const data = await res.json();
        if (data.error) {
          setError(data.error);
        } else {
          setGuesses((prev) => [...prev, data]);
          if (data.won) setWon(true);
        }
      } catch {
        setError("Could not connect to server");
      } finally {
        setLoading(false);
      }
    },
    [gameId]
  );

  return (
    <div className="app">
      <Header />
      <main className="container">
        {!gameId ? (
          <div className="welcome">
            <p className="rules">
              Guess the secret {digitCount}-digit number. Each digit is unique.
            </p>
            <ul className="rules-list">
              <li>
                <strong>Bull</strong> = correct digit in correct position
              </li>
              <li>
                <strong>Cow</strong> = correct digit in wrong position
              </li>
            </ul>
            <button className="btn btn-primary" onClick={startNewGame} disabled={loading}>
              {loading ? "Starting..." : "New Game"}
            </button>
          </div>
        ) : (
          <>
            {won && (
              <div className="win-banner">
                You guessed it in {guesses.length} attempt{guesses.length !== 1 ? "s" : ""}!
              </div>
            )}
            <GameBoard guesses={guesses} digitCount={digitCount} />
            {!won && (
              <GuessInput
                digitCount={digitCount}
                onSubmit={submitGuess}
                disabled={loading}
              />
            )}
            {error && <div className="error">{error}</div>}
            <button
              className="btn btn-secondary"
              onClick={startNewGame}
              disabled={loading}
            >
              New Game
            </button>
          </>
        )}
      </main>
    </div>
  );
}
