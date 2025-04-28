import genanki
import os

class DeckBuilder:
    def __init__(self, deck_id: int, model_id: int, out_pkg: str):
        self.deck_id = deck_id
        self.model_id = model_id
        self.out_pkg = out_pkg

    def build_deck(self, entries):
        model = genanki.Model(
            self.model_id,
            "NO-EN Basic",
            fields=[{"name": "Expression"}, {"name": "Meaning"}, {"name": "Extra"}],
            templates=[{
                "name": "Card 1",
                "qfmt": "{{Expression}}",
                "afmt": "{{FrontSide}}<hr id=answer>{{Meaning}}<br>{{Extra}}",
            }],
        )
        deck = genanki.Deck(self.deck_id, "Norwegian Vocabulary (Full Version)")
        media_files = []
        for e in entries:
            deck.add_note(e.to_note(model))
            if e.audio_tag:
                audio_file = e.audio_tag[7:-1]
                if os.path.exists(audio_file):
                    media_files.append(audio_file)
        genanki.Package(deck, media_files=media_files).write_to_file(self.out_pkg)
        print(f"[SUCCESS] Created Anki package: {self.out_pkg}")
