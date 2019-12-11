class Mixin:
    def clean_text(self, text):
        """Takeout trailing spaces from a given text
        """
        return text.strip()
