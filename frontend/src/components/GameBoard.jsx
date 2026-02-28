export default function GameBoard({ guesses, digitCount }) {
  if (guesses.length === 0) {
    return (
      <div className="board-empty">
        Enter a {digitCount}-digit number with unique digits
      </div>
    );
  }

  return (
    <div className="board">
      <div className="board-header">
        <span className="col-num">#</span>
        <span className="col-guess">Guess</span>
        <span className="col-result">Bulls</span>
        <span className="col-result">Cows</span>
      </div>
      {guesses.map((g, i) => (
        <div key={i} className={`board-row ${g.won ? "board-row-win" : ""}`}>
          <span className="col-num">{i + 1}</span>
          <span className="col-guess guess-digits">
            {g.guess.split("").map((d, j) => (
              <span key={j} className="digit">{d}</span>
            ))}
          </span>
          <span className="col-result bulls">{g.bulls}</span>
          <span className="col-result cows">{g.cows}</span>
        </div>
      ))}
    </div>
  );
}
