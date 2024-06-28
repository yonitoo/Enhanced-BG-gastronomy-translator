import json
import re
from transliterate import translit

def extract_definitional_context(content):
    # добавяме отстояния, за да разделяме правилно изреченията след това
    content_with_spaces = re.sub(r'(?<=[.!?])(?=[А-Я])', '. ', content)
    content_before_equal_sign = content_with_spaces.split("=")[0]
    sentences = re.split(r'(?<=[.!?]) +', content_before_equal_sign)
    if len(sentences) >= 3:
        definitional_context = " ".join(sentences[:3])
    else:
        definitional_context = " ".join(sentences[:len(sentences)])
    return definitional_context


def transliterate_name(name, lang='bg'):
    return translit(name, lang, reversed=True)


def process_contents(content_file):
    with open(content_file, 'r', encoding='utf-8') as file:
        contents = json.load(file)

    terms = {}
    for item in contents:
        title = item['title']
        content = item['content']
        definitional_context = extract_definitional_context(content)

        terms[title] = {
            "definitional_context": definitional_context,
            "transliteration": title
        }

    return terms


def process_contents_and_save(content_file, output_file):
    terms = process_contents(content_file)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({"terms": terms}, file, ensure_ascii=False, indent=4)
    print(f"Processed terms have been saved to {output_file}.")


def main():
    content_file = 'fetched_wiki_fr.json'
    output_file = 'Glossary_fr.json'
    process_contents_and_save(content_file, output_file)


if __name__ == "__main__":
    main()
