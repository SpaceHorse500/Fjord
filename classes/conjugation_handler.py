import requests
import bs4

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

    def try_conjugate(self, word: str) -> dict | None:
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
                variant = parts[0]
                tense_key = " ".join(parts[1:])

                simple_tense = self.TENSE_MAP.get(tense_key.lower())
                if not simple_tense:
                    continue

                verb_form = form_wrap.find('div', class_='meta-form').get_text(strip=True)
                translation = form_wrap.find('div', class_='meta-translation').get_text(strip=True)

                conjugations.setdefault(variant, {})[simple_tense] = f"{verb_form} ({translation})"

            return conjugations if conjugations else None

        except Exception as exc:
            print(f"[ERROR] Conjugation fetch failed for '{word}': {exc}")
            return None
