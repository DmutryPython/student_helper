import spacy
from transformers import pipeline

nlp = spacy.load("ru_core_news_sm")

import config

class TextAnalyzer:
    def __init__(self):
        self.summarizer = pipeline(
            "summarization",
            model=config.SUMMARY_MODEL
        )

    def generate_reference(self, text: str) -> dict:
        """Генерация эталонного ответа"""
        summary = self.summarizer(text, max_length=150)[0]['summary_text']
        # Логика разделения на части
        return {
            "introduction": "...",
            "thesis": "...",
            "conclusion": "..."
        }

    def analyze_structure(self, user_text: str, reference: dict) -> dict:
        """Сравнение структуры ответа"""
        doc = nlp(user_text)
        # Анализ с использованием spaCy
        return {
            "missing_parts": ["заключение"],
            "score": 0.75
        }

    def analyze_parasites(self, text: str) -> dict:
        """Анализ слов-паразитов"""
        doc = nlp(text.lower())
        parasites = [token.text for token in doc if token.text in config.PARASITE_WORDS]

        return {
            "total": len(parasites),
            "frequency": (len(parasites) / len(doc)) * 100,
            "most_common": {"ну": 5, "это": 3}
        }