#!/usr/bin/env python3
"""
Norwegian word list → JSON + Anki .apkg (Auto verb detection + Clean JSON Format)
-----------------------------------------------------------------------------------
Processes words.txt:
- Auto-detect verbs using CoolJugator
- Translation from dictionary.json
- Definitions from NAOB
- Conjugations if verb (clean format)
- Audio via gTTS
- Outputs: vocab.json + NorwegianVocab.apkg
"""

import json
import pathlib
import os
import re
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any, Union

import requests
import bs4
from gtts import gTTS
import genanki
from tqdm import tqdm


class Config:
    DECK_ID = 2059400110
    MODEL_ID = 1607392319
    NAOB_URL = "https://naob.no/ord/"
    WORDS_FILE = "words.txt"
    DICT_FILE = "dictionary.json"
    OUT_JSON = "vocab.json"
    OUT_PKG = "NorwegianVocab.apkg"
    DEFAULT_POS = "noun"


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


class DictionaryHandler:
    def __init__(self, dict_file: str = Config.DICT_FILE):
        self.dict_file = dict_file
        self.dictionary = self._load_dictionary()
        self.normalized_dict = self._create_normalized_dict()
    
    def _load_dictionary(self) -> Dict[str, Union[str, List[str]]]:
        try:
            with open(self.dict_file, 'r', encoding='utf-8') as f:
                print(f"[INFO] Loaded dictionary: {self.dict_file}")
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Loading dictionary: {e}")
            return {}
    
    def _create_normalized_dict(self) -> Dict[str, str]:
        normalized = {}
        for key in self.dictionary:
            normalized[key] = key
            clean_key = re.sub(r'\s*\([^)]*\)', '', key).strip()
            if clean_key != key:
                normalized[clean_key] = key
            matches = re.findall(r'([^\s(]+)\s*\(([^)]+)\)', key)
            for main, alt in matches:
                normalized.setdefault(main, key)
                normalized.setdefault(alt, key)
        return normalized
    
    def get_translation(self, word: str) -> str:
        if word in self.dictionary:
            return self._format_translation(self.dictionary[word])
        if word in self.normalized_dict:
            original_key = self.normalized_dict[word]
            return self._format_translation(self.dictionary[original_key])
        word_lower = word.lower()
        for dict_word in self.normalized_dict:
            if dict_word.lower() == word_lower:
                original_key = self.normalized_dict[dict_word]
                return self._format_translation(self.dictionary[original_key])
        return ""
    
    def _format_translation(self, translation: Union[str, List[str]]) -> str:
        return "; ".join(translation) if isinstance(translation, list) else translation


class DefinitionFetcher:
    @staticmethod
    def get_definition(word: str) -> str:
        try:
            r = requests.get(Config.NAOB_URL + word, timeout=15)
            if r.status_code != 200:
                print(f"[WARN] Definition not found for '{word}'")
                return ""
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            defin_tag = soup.find("span", class_="dictionary-class")
            return defin_tag.text.strip() if defin_tag else ""
        except Exception as exc:
            print(f"[ERROR] Definition fetch failed for {word}: {exc}")
            return ""


class ConjugationHandler:
    TENSE_MAP = {
        "present tense": "present",
        "past tense": "past",
        "future tense": "future",
        "conditional tense": "conditional",
        "imperative tense": "imperative",
        "present perfect tense": "present_perfect",
        "past perfect tense": "past_perfect",
        "future perfect tense": "future_perfect",
        "conditional perfect tense": "conditional_perfect"
    }

    @staticmethod
    def try_conjugate(word: str) -> Optional[Dict[str, Dict[str, str]]]:
        url = f"https://cooljugator.com/no/{word}"
        try:
            resp = requests.get(url, timeout=15)
            if resp.url.endswith("/404"):
                print(f"[INFO] '{word}' not found on CoolJugator.")
                return None

            soup = bs4.BeautifulSoup(resp.text, "html.parser")
            conjugation_section = soup.find('section', id='conjugations')
            if not conjugation_section:
                print(f"[INFO] No conjugation section for '{word}'")
                return None

            conjugations = {}

            tense_titles = conjugation_section.find_all('span', class_='tense-title-space')
            forms_wrappers = conjugation_section.find_all('div', class_='forms-wrapper')

            for title, form_wrap in zip(tense_titles, forms_wrappers):
                full_tense = title.get_text(strip=True)
                parts = full_tense.split()
                if len(parts) < 2:
                    continue
                variant = parts[0]  # Bokmål or Nynorsk
                tense_key = " ".join(parts[1:])

                simple_tense = ConjugationHandler.TENSE_MAP.get(tense_key.lower())
                if not simple_tense:
                    continue

                verb_form = form_wrap.find('div', class_='meta-form').get_text(strip=True)
                translation = form_wrap.find('div', class_='meta-translation').get_text(strip=True)

                if variant not in conjugations:
                    conjugations[variant] = {}
                conjugations[variant][simple_tense] = f"{verb_form} ({translation})"

            if conjugations:
                print(f"[INFO] Conjugations fetched for '{word}'")
                return conjugations
            else:
                print(f"[INFO] No valid conjugations parsed for '{word}'")
                return None

        except Exception as exc:
            print(f"[ERROR] Conjugation fetch failed for '{word}': {exc}")
            return None


class AudioSynthesizer:
    @staticmethod
    def create_audio(word: str) -> str:
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


class DeckBuilder:
    @staticmethod
    def build_deck(entries: List[Entry]) -> None:
        model = genanki.Model(
            Config.MODEL_ID,
            "NO-EN Basic",
            fields=[
                {"name": "Expression"},
                {"name": "Meaning"},
                {"name": "Extra"},
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Expression}}",
                    "afmt": "{{FrontSide}}<hr id=answer>{{Meaning}}<br>{{Extra}}",
                }
            ],
        )
        deck = genanki.Deck(Config.DECK_ID, "Norwegian Vocabulary (Full Version)")
        media_files = []
        for e in entries:
            deck.add_note(e.to_note(model))
            if e.audio_tag:
                audio_file = e.audio_tag[7:-1]
                if os.path.exists(audio_file):
                    media_files.append(audio_file)
        genanki.Package(deck, media_files=media_files).write_to_file(Config.OUT_PKG)
        print(f"[SUCCESS] Created Anki package: {Config.OUT_PKG}")


class VocabProcessor:
    def __init__(self, words_file: str = Config.WORDS_FILE):
        self.words_file = words_file
        self.entries = []
        self.dict_handler = DictionaryHandler()
    
    def read_words(self) -> List[str]:
        try:
            return pathlib.Path(self.words_file).read_text(encoding="utf-8").splitlines()
        except Exception as exc:
            print(f"[ERROR] Reading {self.words_file}: {exc}")
            return []
    
    def process_entries(self) -> None:
        lines = self.read_words()
        for raw in tqdm(lines, desc="Processing"):
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            word = raw.lower()

            pos = Config.DEFAULT_POS
            print(f"\n[PROCESSING] '{word}'")

            conjugations = ConjugationHandler.try_conjugate(word)
            if conjugations:
                pos = "verb"

            translation = self.dict_handler.get_translation(word)
            if not translation:
                print(f"[WARN] No translation found for '{word}'")

            definition = DefinitionFetcher.get_definition(word)
            audio_tag = AudioSynthesizer.create_audio(word)

            self.entries.append(
                Entry(
                    word=word,
                    pos=pos,
                    translation=translation,
                    definition=definition,
                    conjugations=conjugations,
                    audio_tag=audio_tag,
                )
            )
    
    def save_json(self) -> None:
        with open(Config.OUT_JSON, "w", encoding="utf-8") as jf:
            json.dump([asdict(e) for e in self.entries], jf, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Saved JSON to: {Config.OUT_JSON}")
    
    def create_anki_deck(self) -> None:
        DeckBuilder.build_deck(self.entries)
    
    def run(self) -> None:
        if not self.dict_handler.dictionary:
            print("[ERROR] Dictionary is empty or missing.")
            return
        print(f"[INFO] Starting processing of {self.words_file}...")
        self.process_entries()
        if not self.entries:
            print("[ERROR] No entries processed.")
            return
        self.save_json()
        self.create_anki_deck()
        print(f"\n[DONE] Created {len(self.entries)} flashcards")


def main() -> None:
    processor = VocabProcessor()
    processor.run()


if __name__ == "__main__":
    main()
