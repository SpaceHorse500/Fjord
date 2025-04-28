import requests
import bs4

class DefinitionFetcher:
    def __init__(self, naob_url: str):
        self.naob_url = naob_url

    def get_definition(self, word: str) -> str:
        try:
            r = requests.get(self.naob_url + word, timeout=15)
            if r.status_code != 200:
                print(f"[WARN] Definition not found for '{word}'")
                return ""
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            defin_tag = soup.find("span", class_="dictionary-class")
            return defin_tag.text.strip() if defin_tag else ""
        except Exception as exc:
            print(f"[ERROR] Definition fetch failed for {word}: {exc}")
            return ""
