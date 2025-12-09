"""Speech helper for low-latency macOS text-to-speech."""

import os
import subprocess
import sys
import time
from typing import Optional


class SpeechEngine:
    """Reusable speech engine to minimize per-character latency."""

    def __init__(self) -> None:
        self._use_pyobjc = False
        self._synth = None  # type: Optional[object]
        self._warned_fallback = False
        self._warned_no_english_voice = False
        self._say_voice = "Samantha"  # English voice for `say`

        try:
            from AppKit import NSSpeechSynthesizer  # type: ignore

            available = NSSpeechSynthesizer.availableVoices()
            voice_id = self._select_english_voice(available)
            if voice_id is not None:
                self._synth = NSSpeechSynthesizer.alloc().initWithVoice_(voice_id)
                print(f"Using speech engine voice: {voice_id}")
            else:
                self._synth = NSSpeechSynthesizer.alloc().init()
                self._warned_no_english_voice = True
                print(
                    "Warning: No English voice found; using system default voice.",
                    file=sys.stderr,
                )

            self._use_pyobjc = self._synth is not None
        except Exception:
            self._use_pyobjc = False

    @staticmethod
    def _select_english_voice(voices: list) -> Optional[str]:
        """Pick an English voice with locale and quality preferences."""

        def norm_list(vs: list) -> list[str]:
            return [str(v) for v in vs]

        def is_en_us(vid: str) -> bool:
            low = vid.lower()
            return "en-us" in low or "en_us" in low

        def is_en_gb(vid: str) -> bool:
            low = vid.lower()
            return "en-gb" in low or "en_gb" in low

        def is_en_au(vid: str) -> bool:
            low = vid.lower()
            return "en-au" in low or "en_au" in low

        def is_en_other(vid: str) -> bool:
            low = vid.lower()
            return (".en-" in low or ".en_" in low) and not (
                is_en_us(vid) or is_en_gb(vid) or is_en_au(vid)
            )

        def is_enhanced(vid: str) -> bool:
            return "com.apple.voice.enhanced." in vid.lower()

        def is_compact(vid: str) -> bool:
            return "com.apple.voice.compact." in vid.lower()

        def pick_prioritized(cands: list[str]) -> Optional[str]:
            if not cands:
                return None
            sams = [v for v in cands if "samantha" in v.lower()]
            if sams:
                return sorted(sams, key=str.lower)[0]
            return sorted(cands, key=str.lower)[0]

        def choose_for_locale(cands: list[str]) -> Optional[str]:
            if not cands:
                return None
            enhanced = [v for v in cands if is_enhanced(v)]
            choice = pick_prioritized(enhanced)
            if choice:
                return choice
            compact = [v for v in cands if is_compact(v)]
            choice = pick_prioritized(compact)
            if choice:
                return choice
            return pick_prioritized(cands)

        env_voice = os.getenv("SPELL_GYM_VOICE_ID")
        if env_voice:
            env_voice_norm = env_voice.strip().lower()
            for vid in voices:
                if str(vid).lower() == env_voice_norm:
                    return str(vid)

        normalized = norm_list(voices)

        en_us = [v for v in normalized if is_en_us(v)]
        choice = choose_for_locale(en_us)
        if choice:
            return choice

        en_gb = [v for v in normalized if is_en_gb(v)]
        choice = choose_for_locale(en_gb)
        if choice:
            return choice

        en_au = [v for v in normalized if is_en_au(v)]
        choice = choose_for_locale(en_au)
        if choice:
            return choice

        en_other = [v for v in normalized if is_en_other(v)]
        choice = choose_for_locale(en_other)
        if choice:
            return choice

        return None

    def speak(self, text: str) -> None:
        if self._use_pyobjc and self._synth is not None:
            self._synth.startSpeakingString_(text)
            while self._synth.isSpeaking():
                time.sleep(0.01)
            return

        if not self._warned_fallback:
            print(
                "pyobjc not found; using slower 'say'. Install deps: pip install -r requirements.txt",
                file=sys.stderr,
            )
            self._warned_fallback = True

        say_voice = os.getenv("SPELL_GYM_SAY_VOICE", self._say_voice)
        try:
            subprocess.run(["say", "-v", say_voice, text], check=True)
        except subprocess.CalledProcessError:
            print(
                f"Warning: Voice '{say_voice}' unavailable; falling back to system default.",
                file=sys.stderr,
            )
            subprocess.run(["say", text], check=True)
        except FileNotFoundError:
            print("Error: macOS 'say' command is not available.", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as exc:
            print(f"Error while running 'say': {exc}", file=sys.stderr)
            sys.exit(1)


_speech_engine = SpeechEngine()


def speak(text: str) -> None:
    """Speak the given text using the configured speech engine."""
    _speech_engine.speak(text)
