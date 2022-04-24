class Localization:
    available_langs = {'jp', 'kr', 'en', 'th', 'tw'}
    def __init__(self, *lang):
        # if isinstance(lang, str):
        #     # convert to set
        #     lang = {lang, }
        try:
            lang = set(lang)
        except TypeError:
            # unhashable object
            lang = {'en'}
        # convert to lower case
        lang = set(map(lambda x: x.lower() if isinstance(x, str) else (), lang))
        if (itxn:=(lang & Localization.available_langs)):
            self.lang = set(map(lambda x: x.capitalize(), itxn))
        else:
            self.lang = {'En'}
    
    def localize(self, *key):
        """Appends the language name to the given keys"""
        # if isinstance(key, str):
        #     key = [key,]
        try:
            return [k + j for j in self.lang for k in key]
        except TypeError:
            return []
        
    @classmethod
    def all_langs(cls):
        return cls(*cls.available_langs)

