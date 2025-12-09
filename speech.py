"""Speech helper for low-latency macOS text-to-speech."""

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
        self._say_voice = "Samantha"  # English voice for `say`

        try:
            from AppKit import NSSpeechSynthesizer  # type: ignore

            self._synth = NSSpeechSynthesizer.alloc().init()
            self._use_pyobjc = True

            voice_id = self._select_english_voice(NSSpeechSynthesizer.availableVoices())
            if voice_id is not None:
                self._synth.setVoice_(voice_id)
        except Exception:
            self._use_pyobjc = False

    @staticmethod
    def _select_english_voice(voices: list) -> Optional[str]:
        """Pick an English voice if available."""
        preferred = [
            "com.apple.speech.synthesis.voice.samantha",
            "com.apple.speech.synthesis.voice.alex",
            "com.apple.speech.synthesis.voice.ava",
            "com.apple.speech.synthesis.voice.victoria",
        ]
        for vid in preferred:
            if vid in voices:
                return vid
        for vid in voices:
            if ".en_" in vid or vid.endswith(".en"):
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

        try:
            subprocess.run(["say", "-v", self._say_voice, text], check=True)
        except subprocess.CalledProcessError:
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
