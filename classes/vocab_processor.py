import pathlib
import json
from typing import List
from tqdm import tqdm
from dataclasses import asdict

from models import Entry
from dictionary_handler import DictionaryHandler
from definition_fetcher import DefinitionFetcher
from conjugation_handler import ConjugationHandler
from audio_synthesizer import AudioSynthesizer
from deck_builder import DeckBuilder

class VocabProcessor:
    def __init__(self, config_path: str = "config.json"):
        # Load config.json
        with open(config_path, "r") as cf:
            self.config = json.load(cf)

        self.words_file = self.config['WORDS_FILE']
        self.entries = []
        self.dict_handler = DictionaryHandler(self.config['DICT_FILE'])
        self.definition_fetcher = DefinitionFetcher(self.config['NAOB_URL'])
        self.conjugation_handler = ConjugationHandler()
        self.audio_synthesizer = AudioSynthesizer()
        self.deck_builder = DeckBuilder(
            deck_id=self.config['DECK_ID'],
            model_id=self.config['MODEL_ID'],
            out_pkg=self.config['OUT_PKG']
        )
        self.default_pos = self.config.get('DEFAULT_POS', 'noun')
        self.out_json = self.config['OUT_JSON']
    
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

            pos = self.default_pos
            print(f"\n[PROCESSING] '{word}'")

            conjugations = self.conjugation_handler.try_conjugate(word)
            if conjugations:
                pos = "verb"

            translation = self.dict_handler.get_translation(word)
            if not translation:
                print(f"[WARN] No translation found for '{word}'")

            definition = self.definition_fetcher.get_definition(word)
            audio_tag = self.audio_synthesizer.create_audio(word)

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
        with open(self.out_json, "w", encoding="utf-8") as jf:
            json.dump([asdict(e) for e in self.entries], jf, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Saved JSON to: {self.out_json}")
    
    def create_anki_deck(self) -> None:
        self.deck_builder.build_deck(self.entries)
    
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
