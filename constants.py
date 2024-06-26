import os

TARGET_LANG = "EN-GB"
TAG_HANDLING = "html"
DO_NOT_TRANSLATE_TERMS_JSON_FILENAME = "Glossary_cleaned_all.json"
STEMMER_FILE = "bulstem_stemming_rules/stem_rules_context_2_utf8.txt"
TEXT_CORRECTOR_MODEL = "t5-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy_key")
OPENAI_MODEL = "gpt-4o"
