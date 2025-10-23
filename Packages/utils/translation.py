"""
Système de traduction pour PipeZer
Support pour français, anglais et espagnol
"""

import json
import os
from typing import Dict, Any

class TranslationManager:
    """Gestionnaire de traduction pour l'application PipeZer"""
    
    def __init__(self):
        self.current_language = "en"  # Default language
        self.translations = {}
        self.load_translations()
        
    def load_translations(self):
        """Charge toutes les traductions depuis les fichiers JSON"""
        languages = ["fr", "en", "es"]
        
        for lang in languages:
            try:
                # Chemin vers le fichier de traduction
                translation_file = os.path.join(
                    os.path.dirname(__file__), 
                    "translations", 
                    f"{lang}.json"
                )
                
                if os.path.exists(translation_file):
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                else:
                    print(f"Fichier de traduction manquant: {translation_file}")
                    self.translations[lang] = {}
                    
            except Exception as e:
                print(f"Erreur lors du chargement de la traduction {lang}: {e}")
                self.translations[lang] = {}
    
    def set_language(self, language: str):
        """Définit la langue actuelle"""
        if language in self.translations:
            self.current_language = language
            self.save_language_preference()
    
    def load_language(self, language: str):
        """Charge une langue (alias pour set_language pour compatibilité)"""
        self.set_language(language)
    
    def get_text(self, key: str, **kwargs) -> str:
        """Récupère le texte traduit pour la clé donnée"""
        try:
            # Navigation dans la structure JSON (ex: "preferences.title")
            keys = key.split('.')
            text = self.translations[self.current_language]
            
            for k in keys:
                text = text[k]
            
            # Formatage avec les paramètres fournis
            if kwargs:
                return text.format(**kwargs)
            return text
            
        except (KeyError, TypeError):
            # Fallback vers le français si la clé n'existe pas
            try:
                keys = key.split('.')
                text = self.translations["fr"]
                for k in keys:
                    text = text[k]
                if kwargs:
                    return text.format(**kwargs)
                return text
            except (KeyError, TypeError):
                # Si même le français n'a pas la clé, retourner la clé elle-même
                return key
    
    def save_language_preference(self):
        """Sauvegarde la préférence de langue"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            
            if not os.path.exists(pipezer_dir):
                os.makedirs(pipezer_dir)
            
            prefs_file = os.path.join(pipezer_dir, 'language_prefs.json')
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump({"language": self.current_language}, f, indent=2)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la préférence de langue: {e}")
    
    def load_language_preference(self):
        """Charge la préférence de langue sauvegardée"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            prefs_file = os.path.join(pipezer_dir, 'language_prefs.json')
            
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "language" in data and data["language"] in self.translations:
                        self.current_language = data["language"]
                        
        except Exception as e:
            print(f"Erreur lors du chargement de la préférence de langue: {e}")
    
    def get_available_languages(self) -> Dict[str, str]:
        """Retourne la liste des langues disponibles"""
        return {
            "fr": "Français",
            "en": "English", 
            "es": "Español"
        }

# Instance globale du gestionnaire de traduction
translation_manager = TranslationManager()
