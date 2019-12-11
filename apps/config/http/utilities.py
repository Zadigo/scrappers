class UtilitiesMixin:
    @staticmethod
    def clean(value):
        return str(value).strip()

    @classmethod
    def full_clean(cls, value):
        return cls.clean(value).lower()

    def flatten(self, value):
        accents = {
            'é': 'e',
            'è': 'e',
            'ë': 'e',
            'ê': 'e',
            'ï': 'i',
            'î': 'i',
            'ù': 'u'
        }
        value = self.full_clean(value)
        for letter in accents:
            if letter in accents:
                letter = accents[letter]
                word = word + letter
        return word
