import re

import requests
import json


def fetch_titles_from_category(category, lang='bg'):
    """
    Извлича заглавията от дадена категория на Уикипедия.

    :param category: категория, напр. Българска кухня
    :param lang: езикът на Уикипедия страниците
    :return: заглавия на страници от категория на Уикипедия
    """
    s = requests.Session()
    url = f"https://{lang}.wikipedia.org/w/api.php"
    titles = []
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "max"
    }

    while True:
        response = s.get(url=url, params=params).json()
        members = response['query']['categorymembers']
        for member in members:
            titles.append(member['title'])

        if 'continue' in response:
            params['cmcontinue'] = response['continue']['cmcontinue']
        else:
            break

    return titles


def fetch_article_content(title, lang='bg'):
    """
    Извлича статия от Уикипедия по заглавие

    :param title: заглавие на страницата
    :param lang: езикът на Уикипедия страницата
    :return: статията
    """
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": True,
    }

    response = requests.get(url=url, params=params).json()
    page = next(iter(response['query']['pages'].values()))
    return page.get("extract", "")


# def fetch_article_content_in_english(title):
#     content = fetch_article_content(title, lang='en')
#     return extract_definitional_context_with_embeddings(content)


def save_articles_to_json(titles, filename, lang='bg'):
    articles = []
    for title in titles:
        content = fetch_article_content(title, lang)
        if len(content) > 0:
            content = clean_text(content)
            articles.append({"title": title, "content": content, "language": lang})

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)


def clean_text(text):
    cleaned_text = re.sub(r'\(.*?\)', '', text)
    cleaned_text = cleaned_text.replace('\n', ' ')
    cleaned_text = cleaned_text.replace('"', '')
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text


def main():
    category_bg = "Категория:Българска кухня"
    titles_bg = fetch_titles_from_category(category_bg, 'bg')
    save_articles_to_json(titles_bg, 'fetched_wiki_bg.json', 'bg')

    category_en = "Category:Bulgarian cuisine"
    titles_en = fetch_titles_from_category(category_en, 'en')
    save_articles_to_json(titles_en, 'fetched_wiki_en.json', 'en')


if __name__ == '__main__':
    main()
