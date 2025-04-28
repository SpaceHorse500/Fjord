
# FJORD 🇳🇴
**Norwegian Vocabulary Middleware → JSON + Anki Deck Generator**

**Project Fjord** is a lightweight automation tool designed to convert Norwegian word lists into structured JSON and Anki flashcards. Acting as middleware, it streamlines the process of generating vocabulary decks with translations, conjugations, definitions, and audio — ready for direct import into Anki.

> ⚡ **Note:** Definitions are fetched from **Ordbokene.no** with structured meanings and examples. Translation and conjugation settings are configurable via `config.json`.

---

## 🚀 Workflow

### 📥 Input
- Text file (`words.txt`), supports:
  - Simple word: `løpe`
  - Or word + part of speech: `hus noun`

---

### ⚙️ Processing

- **Translation**:  
  Fast lookups via local JSON dictionary (📖 *Norwegian Mouseover Dictionary*).

- **Definition Handling**:  
  Structured scraping from ⚠️ [Ordbokene.no](https://ordbokene.no/), returning meanings and example sentences.

- **Conjugation Detection**:  
  Auto-detects verbs and scrapes conjugations from 🔗 *Cooljugator*, with configurable support for **Bokmål** and **Nynorsk**.

- **Audio Generation**:  
  Pronunciations generated via 🔊 *gTTS*, cached locally in `/audio` to optimize performance.

---

### 📤 Output
- `output/words.json` — Structured JSON containing:
  - Word, POS, translation, definitions, conjugations, audio tags.
- `output/NorwegianVocab.apkg` — Anki Deck via 🃏 *genanki*:
  - **Front**: Norwegian word + audio
  - **Back**: English translation, conjugations (if verb), definitions.

---

## 📂 Project Structure
```
FJORD/
├── main.py
├── config.json
├── words.txt
├── audio/
├── output/
│   ├── words.json
│   └── NorwegianVocab.apkg
├── resources/
│   └── dictionary.json
└── classes/
    ├── models.py
    ├── dictionary_handler.py
    ├── definition_fetcher.py
    ├── conjugation_handler.py
    ├── audio_synthesizer.py
    ├── deck_builder.py
    └── vocab_processor.py
```

---

## 📦 Resources
- 📖 **Dictionary**: Norwegian Mouseover Dictionary (`resources/dictionary.json`)
- ⚠️ **Definitions**: [Ordbokene.no](https://ordbokene.no/)
- 🔗 **Conjugations**: Cooljugator
- 🔊 **Audio**: gTTS
- 🃏 **Anki Deck Generation**: genanki

---

## ⚡ Quickstart

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add words to `words.txt`.
3. Ensure `resources/dictionary.json` contains your translations.
4. Adjust settings in `config.json` if needed.
5. Run:
   ```bash
   python3 main.py
   ```
6. Import `output/NorwegianVocab.apkg` into Anki.

---

## 🔮 Future Work
- Better parsing and formatting for definitions.
- Config option to **disable translation** if not needed.
- Config option to choose output type: generate only **Anki**, only **JSON**, or **both**.

