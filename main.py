import json
from classes.vocab_processor import VocabProcessor

def main() -> None:
    # Centralized config loading
    with open("config.json", "r", encoding="utf-8") as cf:
        config = json.load(cf)

    processor = VocabProcessor(config)
    processor.run()

if __name__ == "__main__":
    main()
