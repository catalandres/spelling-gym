#!/usr/bin/env python3
"""Spelling drill using macOS speech."""

import pathlib
import random
import sys
import termios
import tty
from typing import List, Tuple


LISTS_DIR = pathlib.Path(__file__).resolve().parent / "lists"


def gather_words(lists_dir: pathlib.Path, file_name: str | None = None) -> List[Tuple[str, List[str]]]:
    """Collect non-empty lines from .txt files under lists_dir.

    If `file_name` is provided, only that file (must end with .txt) is read.
    Otherwise all `*.txt` files under `lists_dir` are used.
    """
    words: List[Tuple[str, List[str]]] = []
    if file_name:
        # Allow filenames provided without the .txt suffix
        if not file_name.endswith(".txt"):
            file_name = f"{file_name}.txt"
        path = lists_dir / file_name
        if not path.exists():
            raise SystemExit(f"Requested file not found: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw:
                continue
            # Support variant spellings separated by ' OR '
            parts = [p.strip() for p in raw.split(" OR ") if p.strip()]
            if not parts:
                continue
            display = parts[0]
            variants = parts
            words.append((display, variants))
    else:
        for path in sorted(lists_dir.glob("*.txt")):
            for line in path.read_text(encoding="utf-8").splitlines():
                raw = line.strip()
                if not raw:
                    continue
                parts = [p.strip() for p in raw.split(" OR ") if p.strip()]
                if not parts:
                    continue
                display = parts[0]
                variants = parts
                words.append((display, variants))
    if not words:
        raise RuntimeError(f"No words found in {lists_dir}")
    return words


from speech import speak


def capture_input_with_audio(prompt: str = "> ", repeat_word: str | None = None) -> Tuple[str, int]:
    """Read characters without echo; speak each one as it is typed.

    Backspace/delete clears the buffer, increments a retry counter, and, if
    provided, re-speaks the current target word.
    Returns (typed_text, retries_from_backspace).
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old_attrs = termios.tcgetattr(fd)
    try:
        new_attrs = termios.tcgetattr(fd)
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(fd, termios.TCSADRAIN, new_attrs)

        typed: List[str] = []
        backspace_retries = 0
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            if ch == "\x03":  # Ctrl-C
                raise KeyboardInterrupt
            if ch in ("\x7f", "\b"):  # Backspace/delete
                typed.clear()
                backspace_retries += 1
                speak("start over")
                if repeat_word:
                    speak(repeat_word)
                continue
            typed.append(ch)
            speak(ch)
        return "".join(typed), backspace_retries
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)


def parse_round_count() -> int:
    """Parse optional first CLI argument as number of words."""
    if len(sys.argv) < 2:
        return 10
    try:
        value = int(sys.argv[1])
    except ValueError:
        raise SystemExit("First argument must be an integer word count")
    if value <= 0:
        raise SystemExit("Word count must be positive")
    return value


def parse_optional_filename() -> str | None:
    """Return optional filename from `sys.argv[2]`, or None if not provided."""
    if len(sys.argv) < 3:
        return None
    return sys.argv[2]


def main() -> None:
    filename = parse_optional_filename()
    words = gather_words(LISTS_DIR, file_name=filename)
    round_count = parse_round_count()
    if len(words) < round_count:
        raise RuntimeError(f"Need at least {round_count} words; found {len(words)} in {LISTS_DIR}")

    game_words = random.sample(words, round_count)
    score = 0
    total_retries = 0

    for idx, (display, variants) in enumerate(game_words, start=1):
        print(f"Word {idx} of {round_count}. Press Enter when you're ready.")
        input()

        print("Listen carefully...")
        speak(display)
        print("Type the spelling; input is hidden and spoken back as you type. Press Enter when done.")
        user_input, retries_from_backspace = capture_input_with_audio(repeat_word=display)
        total_retries += retries_from_backspace
        # Accept any of the variants as correct (case-insensitive match)
        user_input_norm = user_input.lower()
        variants_norm = [v.lower() for v in variants]
        is_correct = user_input_norm in variants_norm
        if is_correct:
            score += 1

        print(f"Target : {display}")
        print(f"You typed: {user_input}")
        print(f"Result : {'correct' if is_correct else 'incorrect'}")
        # Show accepted variants for learning/clarity
        if len(variants) > 1:
            print(f"Accepted variants: {', '.join(variants)}")
        print(f"Score  : {score} / {idx}\n")

        speak(f"You typed {user_input or 'nothing'}")
        speak("The answer is correct" if is_correct else "The answer is not correct")
        speak(f"Score is {score} out of {idx}")

    print(f"Final score: {score} / {round_count}")
    print(f"Total retries: {total_retries}")
    speak(f"Final score {score} out of {round_count}")
    speak(f"Total retries {total_retries}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
