import requests
import bs4

class DefinitionFetcher:
    BASE_URL = "https://ordbokene.no/nob/bm,nn/"

    def get_definition(self, word: str) -> str:
        url = self.BASE_URL + word
        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                print(f"[WARN] Definition not found for '{word}' (HTTP {r.status_code})")
                return ""

            soup = bs4.BeautifulSoup(r.text, "html.parser")

            # Find the first definition block
            definition_block = soup.find("div", class_="definition")

            if not definition_block:
                print(f"[WARN] No definition block found for '{word}'")
                return ""

            # Extract clean text
            definition_text = definition_block.get_text(separator=" ", strip=True)
            print(f"[INFO] Definition fetched for '{word}'")
            return definition_text

        except Exception as exc:
            print(f"[ERROR] Definition fetch failed for '{word}': {exc}")
            return ""
