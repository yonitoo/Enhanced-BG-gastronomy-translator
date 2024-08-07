from flask import Flask, request, render_template_string

from enhanced_translator import translate, postprocess_translation

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
    return render_template_string(TEMPLATE, query=query, translation=translation, footnotes=footnotes)


if __name__ == '__main__':
    app.run(debug=True)
