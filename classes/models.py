from dataclasses import dataclass
from typing import Optional, Dict, Any
import genanki

@dataclass
class Entry:
    word: str
    pos: str
    translation: str
    definition: str
    conjugations: Optional[Dict[str, Dict[str, str]]]
    audio_tag: str

    def to_note(self, model: Any) -> genanki.Note:
        extra = self.definition
        if self.conjugations:
            conj_formatted = ""
            for variant, tenses in self.conjugations.items():
                conj_formatted += f"<b>{variant}</b>:<br>"
                for tense, form in tenses.items():
                    conj_formatted += f"{tense}: {form}<br>"
                conj_formatted += "<br>"
            extra += "<br><pre>" + conj_formatted + "</pre>"
        return genanki.Note(
            model=model,
            fields=[f"{self.word} {self.audio_tag}", self.translation, extra],
        )
