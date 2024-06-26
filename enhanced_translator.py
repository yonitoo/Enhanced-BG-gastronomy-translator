import json
import os
import re

import deepl
from bulstem.stem import BulStemmer
from constants import STEMMER_FILE, DO_NOT_TRANSLATE_TERMS_JSON_FILENAME, TARGET_LANG, TAG_HANDLING, TEXT_CORRECTOR_MODEL
import phunspell

stemmer = BulStemmer.from_file(STEMMER_FILE,
                               min_freq=2, left_context=2)
auth_key = os.getenv("DEEPL_AUTH_KEY")
if not auth_key:
    raise ValueError("DEEPL_AUTH_KEY не е зададен като променлива на средата.")
translator = deepl.Translator(auth_key)
pspell = phunspell.Phunspell('bg_BG')
text_corrector = pipeline("text2text-generation", model=TEXT_CORRECTOR_MODEL)


def correct_spelling(text):
    words = text.split()
    corrected_words = []
    for word in words:
        if not pspell.lookup(word):
            suggestions = list(pspell.suggest(word))
            corrected_words.append(suggestions[0] if suggestions else word)
        else:
            corrected_words.append(word)
    return " ".join(corrected_words)


def load_terms_data(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)["terms"]


def mark_terms_with_no_translate_and_footnotes(text, terms):
    """
    Маркираме термините от речника във заявката с no translate tag и създаваме бележка под линия за всеки.

    :param text: текст/заявка
    :param terms: термини от речника
    :return: текста с маркирани термини, създадените бележки под линия за тях и транслитерациите им
    """
    footnote_index = 1
    footnotes = []
    transliterations_temp = {}
    term_first_positions = {}
    query_words = text.split()
    query_stems = [stemmer.stem(word) for word in query_words]
    for term, data in terms.items():
        definition = data["definitional_context"]
        transliteration = data["transliteration"]
        term = preprocess_text(term)
        term_words = term.split()
        term_stems = [stemmer.stem(word) for word in term_words]
        window_size = len(term_stems)
        for i in range(len(query_stems) - window_size + 1):
            window = query_stems[i:i + window_size]
            if window == term_stems and not any(note[1] == term for note in footnotes):
                term_first_positions[term] = i  # за да подредим термините спрямо първото срещане в заявката
                replacement = f'<span translate="no">{transliteration}</span>({footnote_index})'
                text = text.replace(" ".join(query_words[i:i + window_size]), replacement)
                footnotes.append((footnote_index, term, definition))
                transliterations_temp[footnote_index] = transliteration
                footnote_index += 1

    footnotes.sort(key=lambda note: term_first_positions[note[1]])

    return text, footnotes, transliterations_temp


def replace_span_with_transliteration(text, transliterations_temp):
    """
    Маха no translate тага.

    :param text: текст
    :param transliterations_temp: временно взетите транслитерации от речника
    :return: текст без no translate тагове
    """
    for index, translit in transliterations_temp.items():
        text = text.replace(f'<span translate="no">{translit}</span>', translit)
    return text


def translate_and_transliterate_definitions(footnotes, transliterations, translator, target_lang="EN-GB"):
    """
    Превежда бележките под линия без термините в тях, термините транслитерира.

    :param footnotes: бележки под линия
    :param transliterations: транслитерации на термини
    :param translator: преводач
    :param target_lang: езика, на когото превеждаме
    :return: преведени бележки под линия
    """
    translated_footnotes = []
    for index, term, definition in footnotes:
        term_stems = [stemmer.stem(word) for word in term.split()]
        definition = preprocess_text(definition)
        definition_words = definition.split()

        window_size = len(term_stems)
        for i in range(len(definition_words) - window_size + 1):
            window = [stemmer.stem(word) for word in definition_words[i:i + window_size]]
            if window == term_stems:
                term_start = definition.find(" ".join(definition_words[i:i + window_size]))
                term_end = term_start + len(" ".join(definition_words[i:i + window_size]))
                replacement = f'<span translate="no">{transliterations[index]}</span>'
                definition = definition[:term_start] + replacement + definition[term_end:]
        # Превеждаме дефинитивния контекст
        try:
            result = translator.translate_text(definition, target_lang=target_lang)
            result.text = result.text.replace(f'<span translate="no">{transliterations[index]}</span>',
                                              transliterations[index])
        except deepl.DeepLException as e:
            print(f"Грешка при превода на '{definition}': {e}")
            translated_footnotes.append((index, definition))
        else:
            translated_footnotes.append((index, result.text))
    return translated_footnotes


def add_footnotes_to_translation(translated_text, footnotes):
    """
    Добавя преведените бележки под линия към превода на заявката.

    :param translated_text: превод на заявката
    :param footnotes: бележки под линия
    :return: превод с бележки под линия
    """

    for index, translated_definition in footnotes:
        footnote = f"({index}) {translated_definition}"
        translated_text += f"\n{footnote}"
    return translated_text


def preprocess_text(text):
    """
    Разделя препинателни знаци от думите, за да не обърка намирането на корен на думите.

    :param text: текст
    :return: текст с разделени препинателни знаци от думите
    """
    # Добавя интервал преди и след всяка запетая, точка, въпросителен и удивителен знак
    text = re.sub(r'([,.!?])', r' \1 ', text)
    # Добавя интервал при този тип кавични
    for i, char in enumerate(text):
        if char in ['\'', '\"']:
            if len(text) >= i:
                text = text[:i] + ' ' + char + ' ' + text[i+1:]
            else:
                text = text[:i] + ' ' + char
    for i, char in enumerate(text):
        if char in ['„', '“'] and not 'a' <= text[i + 1] <= 'z':
            if len(text) >= i:
                text = text[:i] + ' ' + char + ' ' + text[i+1:]
            else:
                text = text[:i] + ' ' + char,
    # Съкращава последователности от интервали до един
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def postprocess_translation(translation):
    """
    Премахва интервали преди пунктуационни знаци.

    :param translation: превод за преработване
    :return: преработен превод
    """
    translation = re.sub(r'\s+([,.!?])', r'\1', translation)
    return translation


def translate(query):
    """
    Превежда заявка като обяснява термините, които са в гастрономичния речник.

    :param query: заявката за превеждане
    :return: Превод на заявката с обяснени термини в нея.
    """
    query = preprocess_text(query)
    query = correct_spelling(query)
    print(query)
    # зареждаме речника
    terms = load_terms_data(DO_NOT_TRANSLATE_TERMS_JSON_FILENAME)
    # Маркиране на термините от речника с no translate tag
    text_with_no_translate_tags, footnotes, transliterations_temp = mark_terms_with_no_translate_and_footnotes(query,
                                                                                                               terms)
    # Превод на основния текст
    translated_text = translator.translate_text(text_with_no_translate_tags,
                                                target_lang=TARGET_LANG, tag_handling=TAG_HANDLING).text
    # Премахване на no translate tags и заместване с транслитерация
    translated_text = replace_span_with_transliteration(translated_text, transliterations_temp)
    translated_text = postprocess_translation(translated_text)
    # Превод и транслитерация на дефинитивните контексти
    translated_footnotes = translate_and_transliterate_definitions(footnotes, transliterations_temp, translator)
    # Добавяне на преведените бележки под линия към превода
    final_translation = add_footnotes_to_translation(translated_text, translated_footnotes)
    # Форматираме пунктуацията
    final_translation = postprocess_translation(final_translation)
    return final_translation, translated_text, translated_footnotes


def main():
    # query = input("Въведете каквото желаете да преведете: ")  # TODO sys input encoding проблем с някои думи
    query = "Баница със сирене и сладко от малини за закуска, качамак за обяд и Руло Стефани за вечеря."
    translation, _, _ = translate(query)
    print(translation)


if __name__ == "__main__":
    main()
