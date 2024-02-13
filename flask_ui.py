import os

import deepl
from bulstem.stem import BulStemmer
from flask import Flask, request, render_template_string

from enhanced_translator_stem import translate, postprocess_translation

# stemmer = BulStemmer.from_file('./bulstem_stemming_rules/stem_rules_context_2_utf8.txt',
#                                min_freq=2, left_context=2)
# auth_key = os.getenv("DEEPL_AUTH_KEY")
# if not auth_key:
#     raise ValueError("DEEPL_AUTH_KEY не е зададен като променлива на средата.")
# translator = deepl.Translator(auth_key)
# target_lang = "EN-GB"
# tag_handling = "html"
# do_not_translate_terms_json_filename = "Glossary_cleaned.json"
app = Flask(__name__)

TEMPLATE = '''
<html>
    <head>
        <title>BG-!Translate-simplified</title>
    </head>
    <body>
        <h2>Подсилен превод в сферата на гастрономията</h2>
        <form method="POST">
            <input type="text" name="query" placeholder="Въведете текст за превод:" style="width: 300px;"/>
            <input type="submit" value="Translate" />
        </form>
        {% if query %}
            <h3>Заявка:</h3>
            <p>{{ query | safe }}</p>
        {% endif %}
        {% if translation %}
            <h3>Превод:</h3>
            <p>{{ translation | safe }}</p>
        {% endif %}
        {% if footnotes %}
            <h3>Разяснения:</h3>
            <ol>
            {% for footnote in footnotes | reverse %}
                ({{ footnote[0] | safe }}) {{ footnote[1] | safe }}<br>
            {% endfor %}
            </ol>
        {% endif %}
    </body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def home():
    query = ""
    translation = ""
    footnotes = []
    if request.method == 'POST':
        query = request.form['query']
        _, translation, footnotes = translate(query)
        translation = postprocess_translation(translation)
        for footnote in footnotes:
            postprocess_translation(footnote[1])
    return render_template_string(TEMPLATE, query=query, translation=translation, footnotes=footnotes)


if __name__ == '__main__':
    app.run(debug=True)
