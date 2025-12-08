#!/usr/bin/env python3
"""Ten-word spelling drill using macOS speech."""

import pathlib
import random
import sys
import termios
import tty
from typing import List


LISTS_DIR = pathlib.Path(__file__).resolve().parent / "lists"


def gather_words(lists_dir: pathlib.Path) -> List[str]:
    """Collect non-empty lines from all .txt files under lists_dir."""
    words: List[str] = []
    for path in sorted(lists_dir.glob("*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.strip()
            if word:
                words.append(word)
    if not words:
        raise RuntimeError(f"No words found in {lists_dir}")
    return words


from speech import speak


def capture_input_with_audio(prompt: str = "> ") -> str:
    """Read characters without echo; speak each one as it is typed."""
    sys.stdout.write(prompt)
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old_attrs = termios.tcgetattr(fd)
    try:
        new_attrs = termios.tcgetattr(fd)
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(fd, termios.TCSADRAIN, new_attrs)

        typed: List[str] = []
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            if ch == "\x03":  # Ctrl-C
                raise KeyboardInterrupt
            if ch in ("\x7f", "\b"):  # Backspace/delete
                if typed:
                    typed.pop()
                    speak("backspace")
                continue
            typed.append(ch)
            speak(ch)
        return "".join(typed)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)


def main() -> None:
    words = gather_words(LISTS_DIR)
    round_count = 10
    if len(words) < round_count:
        raise RuntimeError(f"Need at least {round_count} words; found {len(words)} in {LISTS_DIR}")

    game_words = random.sample(words, round_count)
    score = 0

    for idx, target in enumerate(game_words, start=1):
        print(f"Word {idx} of {round_count}: listen carefully...")
        speak(target)
        print("Type the spelling; input is hidden and spoken back as you type. Press Enter when done.")

        user_input = capture_input_with_audio()
        is_correct = user_input == target
        if is_correct:
            score += 1

        print(f"Target : {target}")
        print(f"You typed: {user_input}")
        print(f"Result : {'correct' if is_correct else 'incorrect'}")
        print(f"Score  : {score} / {idx}\n")

        speak(f"You typed {user_input or 'nothing'}")
        speak("The answer is correct" if is_correct else "The answer is not correct")
        speak(f"Score is {score} out of {idx}")

    print(f"Final score: {score} / {round_count}")
    speak(f"Final score {score} out of {round_count}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
