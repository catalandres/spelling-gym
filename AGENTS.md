# Agents

_Maintenance_: Keep this file and `README.md` up to date with behavior changes. Markdown files must comply with markdownlint conventions.

## Spelling Drill CLI

- **Purpose**: Practice spelling by hearing random words from the `lists` directory, typing them without on-screen echo, and getting immediate correctness feedback with audio.
- **Flow**:
  1) Pick N different words (default 10; configurable via first CLI argument) uniformly at random from all `.txt` files under `lists/` (one word per line expected).
  2) Speak each word aloud using the speech engine (PyObjC NSSpeechSynthesizer when available), picking English voices in this order: enhanced en-US (Samantha preferred), compact en-US (Samantha preferred), en-GB, en-AU, then other English; falls back to macOS `say` only if needed.
  3) Before each word, prompt the user to press Enter to begin; then speak the word.
  4) Prompt the user to type the spelling; characters are not echoed to the terminal.
  5) Each typed character is spoken back via the speech engine so the user hears their input. Pressing Backspace clears the current attempt, replays the word, counts a retry, and lets the user restart that word input.
  6) On Enter, display the target word, the user input, and whether the attempt was correct; also speak what was typed, whether it was correct, and the running score. If incorrect, move on to the next word (no re-tries for wrong answers).
  7) After all words, print and speak the final score and total retries (backspaces).
- **Requirements**: macOS with speech available; Python 3.8+; PyObjC installed for low-latency speech (fallback to `say` if missing).
- **Run**: `python3 spell.py`
- **Future**: Add configurable voices/rates and alternate scoring modes.
