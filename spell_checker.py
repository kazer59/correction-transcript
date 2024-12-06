from spellchecker import SpellChecker
import re
import string

class SpellCheckerManager:
    def __init__(self, language='fr'):
        self.spell = SpellChecker(language=language)
        
    def check_word(self, word):
        """Vérifie si un mot est correctement orthographié"""
        # Si le mot contient une apostrophe, on le vérifie en entier
        if "'" in word:
            clean_word = word.strip(string.punctuation).lower()
            return True  # On considère les mots avec apostrophe comme corrects
            
        clean_word = word.strip(string.punctuation).lower()
        if len(clean_word) <= 2 or clean_word.isdigit():
            return True
        return self.spell.correction(clean_word) == clean_word
        
    def get_suggestions(self, word):
        """Retourne les suggestions pour un mot mal orthographié"""
        clean_word = word.strip(string.punctuation).lower()
        return self.spell.candidates(clean_word)
        
    def extract_words(self, text):
        """Extrait les mots d'un texte en conservant la ponctuation pour le remplacement"""
        # Utilise une expression régulière qui capture les mots avec apostrophe comme un seul mot
        return re.finditer(r'\b([a-zA-ZÀ-ÿ]+(?:\'[a-zA-ZÀ-ÿ]+)?)([\s\.,;:!?\'\"]*)', text)
