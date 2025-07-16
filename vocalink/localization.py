import json
import os

class LocalizationManager:
    """Manages loading and providing localized strings."""

    def __init__(self, default_language="en"):
        self.translations = {}
        self.current_language = default_language
        self.load_translations(default_language)

    def load_translations(self, language):
        """Loads translation strings for the specified language."""
        locales_dir = os.path.join(os.path.dirname(__file__), '..', 'locales')
        file_path = os.path.join(locales_dir, f'{language}.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = language
            print(f"Loaded translations for: {language}", flush=True)
        except FileNotFoundError:
            print(f"Translation file not found for {language}: {file_path}", flush=True)
            # Fallback to default language if translation not found
            if language != "en":
                self.load_translations("en")
            else:
                self.translations = {} # No translations available
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}", flush=True)
            if language != "en":
                self.load_translations("en")
            else:
                self.translations = {} # No translations available

    def get_string(self, key, *args):
        """Retrieves a translated string for the given key."""
        s = self.translations.get(key, key) # Fallback to key if not found
        return s.format(*args)

    def get_available_languages(self):
        """Returns a list of available languages based on JSON files in the locales directory."""
        locales_dir = os.path.join(os.path.dirname(__file__), '..', 'locales')
        languages = []
        if os.path.exists(locales_dir):
            for filename in os.listdir(locales_dir):
                if filename.endswith('.json'):
                    languages.append(os.path.splitext(filename)[0])
        return sorted(languages)
