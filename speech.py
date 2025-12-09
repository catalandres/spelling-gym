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
        """Pick an English voice if available (robust to locale naming)."""
        preferred = [
            "com.apple.speech.synthesis.voice.samantha.premium",
            "com.apple.speech.synthesis.voice.samantha",
            "com.apple.speech.synthesis.voice.alex",
            "com.apple.speech.synthesis.voice.ava.premium",
            "com.apple.speech.synthesis.voice.ava",
            "com.apple.speech.synthesis.voice.victoria",
            "com.apple.speech.synthesis.voice.kate",
            "com.apple.speech.synthesis.voice.serena",
            "com.apple.speech.synthesis.voice.daniel",
            "com.apple.speech.synthesis.voice.moira",
        ]

        def is_english(voice_id: str) -> bool:
            low = voice_id.lower()
            return (
                "samantha" in low
                or "alex" in low
                or "ava" in low
                or "victoria" in low
                or "kate" in low
                or "serena" in low
                or "daniel" in low
                or "moira" in low
                or ".en_" in low
                or ".en-" in low
                or low.endswith(".english")
            )

        env_voice = os.getenv("SPELL_GYM_VOICE_ID")
        if env_voice:
            env_voice_norm = env_voice.strip().lower()
            for vid in voices:
                if str(vid).lower() == env_voice_norm:
                    return str(vid)

        normalized = [str(v) for v in voices]

        for vid in preferred:
            if vid in normalized:
                return vid
        for vid in normalized:
            if is_english(vid):
                return vid
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
