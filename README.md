
# FJORD 🇳🇴
**Norwegian Vocabulary Middleware → JSON + Anki Deck Generator**

Project Fjord is a lightweight automation tool designed to convert Norwegian word lists into structured JSON and Anki flashcards. Acting as middleware, it streamlines the process of generating vocabulary decks with translations, conjugations, and audio — ready for direct import into Anki.

> ⚡ **Note:** The current version focuses on translations. Definition fetching (via NAOB) is unreliable and under consideration for removal or replacement.

---

## 🚀 Workflow

### 📥 Input
- Text file (`words.txt`), supports:
  - Simple word: `løpe`
  - Or word + pos format: `hus`

---

### ⚙️ Processing

- **Translation**:  
  Fast lookups via local JSON dictionary (📖 *Norwegian Mouseover Dictionary*).

- **Definition Handling**:  
  XXX scraping is unstable.  
  *Future:* Skip definitions or derive English-based definitions from translations.

- **Conjugation Detection**:  
  Auto-detects verbs and scrapes conjugations from 🔗 *Cooljugator*.

- **Audio Generation**:  
  Pronunciations via 🔊 *gTTS*, with local caching to avoid redundancy.

---

### 📤 Output
- `vocab.json` — Structured JSON
- `NorwegianVocab.apkg` — Anki Deck via 🃏 *genanki*
  - **Front**: Norwegian word + audio
  - **Back**: English translation (+ conjugations if verb)

---

## 🎨 Design Philosophy
- 🛠️ **Middleware-Only**: No GUI. Pure backend automation for Anki imports.
- ⚡ **Offline-First**: Uses local resources where possible for speed & reliability.
- 🎯 **Focused**: No bloat — efficient vocabulary deck generation.

---

## 📂 Project Structure
```
FJORD/
├── main.py
├── config.json
├── models.py
├── dictionary_handler.py
├── definition_fetcher.py
├── conjugation_handler.py
├── audio_synthesizer.py
├── deck_builder.py
├── vocab_processor.py
├── words.txt
└── dictionary.json
```

---

## 📦 Resources
- 📖 **Dictionary**: Norwegian Mouseover Dictionary
- 🔊 **Audio**: gTTS
- 🃏 **Anki Deck**: genanki
- 🔗 **Conjugations**: Cooljugator
- ⚠️ **Definitions**: (unstable)
- 🌐 **Optional API**: Lingvanex

---

## ⚡ Quickstart

1. Add words to `words.txt`
2. Fill `dictionary.json` with translations
3. Run:
   ```bash
   python3 main.py
   ```
4. Import `NorwegianVocab.apkg` into Anki.

---

## 🎯 Conclusion
Project **Fjord** is a lean, purpose-built middleware tool to automate the generation of Norwegian vocabulary flashcards. With translations, conjugations, and audio embedded, it eliminates manual work — delivering ready-to-import Anki decks for efficient language learning.

