# Spelling Gym (10-Word Game)

A tiny practice script: the computer says 10 random words, you type them without seeing what you type, and it tells you (and says aloud) if you got each one right.

## What you need (macOS)

- A Mac.
- Homebrew installed.
- Python from Homebrew.
- Internet for the first install.

## One-time setup (with a safe venv)

1) Open Terminal.
2) Install Python: `brew install python`.
3) Go to this folder. Example: `cd /Users/<something>/spelling-gym`.
4) Make a private Python box (venv): `python3 -m venv .venv`.
5) Turn it on: `source .venv/bin/activate` (you will see `(.venv)` in the prompt).
6) Upgrade pip so installs go smoothly: `python3 -m pip install --upgrade pip`.
7) Install the needed voice helper: `pip install -r requirements.txt`.
   - This installs `pyobjc`, which makes the voice fast. If it ever fails, you can still run the game; it will fall back to macOS `say` but may be slower.

## How to run a practice round (10 words)

1) Make sure the venv is on. If you see `(.venv)` in your prompt, you are good. If not, run `source .venv/bin/activate` from this folder.
2) Start the game: `python3 spell.py`.
3) For each of the 10 words:
   - Listen: the computer will say a word.
   - Type the word. You will not see the letters, but you will hear each letter you type.
     - If you make a mistake, press Backspace; you will hear "backspace".
   - Press Enter when you finish the word.
   - The screen will show the target word, what you typed, and if it was correct.
   - The computer will also say what you typed, say if it was correct or not, and say your score so far.
4) At the end of 10 words, the screen (and the computer) will tell you your final score.

## Tips

- Turn up your Mac volume if you cannot hear it.
- If you close Terminal or start a new one, run `source .venv/bin/activate` again before playing.
- If the game says it is using the slower `say`, install PyObjC with `pip install -r requirements.txt` while the venv is active.
- The voice picker prefers enhanced U.S. English voices (Samantha if available), then compact U.S., then UK, then AU, then other English voices. It prints the voice it chose when you start. You can force a specific engine voice with `SPELL_GYM_VOICE_ID=<voice-id>` and a `say` fallback voice with `SPELL_GYM_SAY_VOICE=<Name>` when running `python3 spell.py`.
- Stop anytime with `Ctrl + C` while the program is waiting for input.

## What is next (future ideas)

- Picking different voices and speeds.
