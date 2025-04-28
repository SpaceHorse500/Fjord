import pathlib
import json
from typing import List
from tqdm import tqdm
from dataclasses import asdict

from classes.models import Entry
from classes.dictionary_handler import DictionaryHandler
from classes.definition_fetcher import DefinitionFetcher
from classes.conjugation_handler import ConjugationHandler
from classes.audio_synthesizer import AudioSynthesizer
from classes.deck_builder import DeckBuilder

class VocabProcessor:
    def __init__(self, config: dict):
        self.config = config

        self.words_file = config['WORDS_FILE']
        self.entries = []
        self.dict_handler = DictionaryHandler(config['DICT_FILE'])
        self.definition_fetcher = DefinitionFetcher(config['NAOB_URL'])
        self.conjugation_handler = ConjugationHandler()
        self.audio_synthesizer = AudioSynthesizer()
        self.deck_builder = DeckBuilder(
            deck_id=config['DECK_ID'],
            model_id=config['MODEL_ID'],
            out_pkg=config['OUT_PKG']
        )
        self.default_pos = config.get('DEFAULT_POS', 'noun')
        self.out_json = config['OUT_JSON']
        self.variants = config.get('VARIANTS', {"Bokmål": True})
        self.enable_translation = config.get('ENABLE_TRANSLATION', True)
    
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
            selected_conjugations = None

            if conjugations:
                pos = "verb"
                selected_conjugations = {}
                for variant, include in self.variants.items():
                    if include and variant in conjugations:
                        selected_conjugations[variant] = conjugations[variant]

                if not selected_conjugations:
                    print(f"[WARN] No selected variants found for '{word}'. Using all available.")
                    selected_conjugations = conjugations

            if self.enable_translation:
                translation = self.dict_handler.get_translation(word)
                if not translation:
                    print(f"[WARN] No translation found for '{word}'")
            else:
                translation = ""

            definition = self.definition_fetcher.get_definition(word)
            audio_tag = self.audio_synthesizer.create_audio(word)

            self.entries.append(
                Entry(
                    word=word,
                    pos=pos,
                    translation=translation,
                    definition=definition,
                    conjugations=selected_conjugations,
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
