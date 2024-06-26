import json
import re
from transliterate import translit

REMOVE_TERMS = [
    "Българска кухня", "Баница със спанак и сирене", "Градинска чубрица", "Джоджен",
    "Картофена салата", "Шницел", "Яйца на очи", "Червен пипер", "Чорба от коприва",
    "Кюфтета с кашкавал", "Палачинка", "Печен боб", "Печени картофи", "Поничка",
    "Свинско с ориз", "Свинско със зеле", "Пиле с ориз", "Кюфте", "Копривщенска кухня"
]

# Function to apply predefined modifications
def apply_modifications(title, definitional_context):
    modifications = {
        "Елена (филе)": ("Филе Елена", translit("Филе Елена", 'bg', reversed=True)),
        "Мешана скара": (definitional_context.replace(
            "Кебапче Кюфте Шишчета Пържола Наденичка КарначеСервира се",
            "Кебапче, Кюфте, Шишчета, Пържола, Наденичка, Карначе. Сервира се"
        ), translit("Мешана скара", 'bg', reversed=True)),
        "Пача (супа)": ("Супа пача", translit("Супа пача", 'bg', reversed=True)),
        "Принцеса (храна)": ("Принцеса", translit("Принцеса", 'bg', reversed=True)),
        "Снежанка (салата)": ("Снежанка", translit("Снежанка", 'bg', reversed=True)),
        "Торта \"Гараш\"": ("Торта Гараш", translit("Торта Гараш", 'bg', reversed=True)),
        "Руло \"Стефани\"": ("Руло Стефани", translit("Руло Стефани", 'bg', reversed=True)),
    }
    if title in modifications:
        title, transliteration = modifications[title]
    else:
        transliteration = translit(title, 'bg', reversed=True)
    return title, definitional_context, transliteration


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


def transliterate_name(name):
    return translit(name, 'bg', reversed=True)


def process_contents(content_file):
    with open(content_file, 'r', encoding='utf-8') as file:
        contents = json.load(file)

    terms = {}
    for item in contents:
        title = item['title']
        if title in REMOVE_TERMS:
            continue
        content = item['content']
        definitional_context = extract_definitional_context(content)
        title, definitional_context, transliterated_name = apply_modifications(title, definitional_context)

        terms[title] = {
            "definitional_context": definitional_context,
            "transliteration": transliterated_name
        }

    terms["Шарена сол"] = {
        "definitional_context": "Sharena sol is a traditional Bulgarian spice blend, typically made with a mix of dried savory, paprika, salt, and fenugreek.",
        "transliteration": "Sharena sol"
    }

    terms["Кашкавал пане"] = {
        "definitional_context": "Кашкавал пане е традиционно българско ястие, приготвено от узрял кашкавал, нарязан на квадрати или правоъгълници, оваляни в брашно, панировка от галета , които след това последователно се потапят в разбити яйца и се пържи в сгорещено растително масло до получаване на златиста коричка. Може да се сервира като предястие или основно ястие.",
        "transliteration": "Kashkaval pane"
    }

    return terms


def process_contents_and_save(content_file, output_file):
    terms = process_contents(content_file)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({"terms": terms}, file, ensure_ascii=False, indent=4)
    print(f"Processed terms have been saved to {output_file}.")


def main():
    content_file = 'fetched_wiki_bg.json'
    output_file = 'Glossary_2.json'
    process_contents_and_save(content_file, output_file)


if __name__ == "__main__":
    main()
