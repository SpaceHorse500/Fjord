import json
import re
from typing import Dict, Union

class DictionaryHandler:
    def __init__(self, dict_file: str):
        self.dict_file = dict_file
        self.dictionary = self._load_dictionary()
        self.normalized_dict = self._create_normalized_dict()
    
    def _load_dictionary(self) -> Dict[str, Union[str, list]]:
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
    
    def _format_translation(self, translation: Union[str, list]) -> str:
        return "; ".join(translation) if isinstance(translation, list) else translation
