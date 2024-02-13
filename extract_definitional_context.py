import json
import re
from transliterate import translit

content_file = 'fetched_wiki_bg.json'


def extract_definitional_context(content):
    # добавяме отстояния, за да разделяме правилно изреченията след това
    content_with_spaces = re.sub(r'(?<=[.!?])(?=[А-Я])', '. ', content)
    content_before_equal_sign = content_with_spaces.split("=")[0]
    sentences = re.split(r'(?<=[.!?]) +', content_before_equal_sign)
    definitional_context = " ".join(sentences[:2])
    return definitional_context


def transliterate_name(name):
    return translit(name, 'bg', reversed=True)


def process_contents(content_file):
    with open(content_file, 'r', encoding='utf-8') as file:
        contents = json.load(file)

    terms = {}
    for item in contents:
        title = item['title']
        content = item['content']
        definitional_context = extract_definitional_context(content)
        transliterated_name = transliterate_name(title)

        terms[title] = {
            "definitional_context": definitional_context,
            "transliteration": transliterated_name
        }

    return terms


def process_contents_and_save(output_file):
    terms = process_contents(content_file)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({"terms": terms}, file, ensure_ascii=False, indent=4)
    print(f"Processed terms have been saved to {output_file}.")


def main():
    output_file = 'Glossary.json'
    process_contents_and_save(output_file)


if __name__ == "__main__":
    main()
