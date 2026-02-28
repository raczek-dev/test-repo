import { useState, useRef, useEffect } from "react";

export default function GuessInput({ digitCount, onSubmit, disabled }) {
  const [value, setValue] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [disabled]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.length !== digitCount) return;
    if (new Set(value).size !== digitCount) return;
    if (!/^\d+$/.test(value)) return;
    onSubmit(value);
    setValue("");
  };

  const isValid =
    value.length === digitCount &&
    /^\d+$/.test(value) &&
    new Set(value).size === digitCount;

  return (
    <form className="guess-form" onSubmit={handleSubmit}>
      <input
        ref={inputRef}
        type="text"
        inputMode="numeric"
        pattern="[0-9]*"
        maxLength={digitCount}
        value={value}
        onChange={(e) => setValue(e.target.value.replace(/\D/g, ""))}
        placeholder={`Enter ${digitCount} digits`}
        disabled={disabled}
        className="guess-input"
        autoComplete="off"
      />
      <button
        type="submit"
        className="btn btn-primary"
        disabled={disabled || !isValid}
      >
        Guess
      </button>
    </form>
  );
}
