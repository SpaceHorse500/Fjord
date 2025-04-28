import os
import re
from gtts import gTTS

class AudioSynthesizer:
    def create_audio(self, word: str) -> str:
        os.makedirs("audio", exist_ok=True)
        clean_word = re.sub(r'\s*\([^)]*\)', '', word).strip()
        filename = f"audio/{clean_word}.mp3"
        try:
            if not os.path.exists(filename):
                gTTS(text=clean_word, lang="no").save(filename)
                print(f"[INFO] Audio generated for '{word}'")
            else:
                print(f"[INFO] Audio cached for '{word}'")
            return f"[sound:{filename}]"
        except Exception as exc:
            print(f"[ERROR] Audio generation failed for {word}: {exc}")
            return ""
