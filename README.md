# Enhanced-BG-gastronomy-translator

## Overview

This project is focused on the domain of gastronomy. Its purpose is to enhance the translation of some Bulgarian 
cuisine-related terms by not just transliterating them into English. Instead, we are explaining them in order to 
give the foreigners a brief idea what the dish looks like.

## Motivation

Most of the restaurants in Bulgaria, especially local, traditional ones, don't offer English menu. 
Many of the ones that do, just mention the names of some typical Bulgarian dishes and do not provide details.
Therefore, a foreigner would have to search online or ask someone for the description of each dish. 
This is where the motivation for this project comes for - to help the tourists and not only them to navigate better
when going to the restaurant.

## Dependencies

BulStem: https://pypi.org/project/bulstem/

```
Nakov, P. BulStem: Design and evaluation of inflectional stemmer for Bulgarian. In Workshop on
Balkan Language Resources and Tools (Balkan Conference in Informatics).
```
Install it using pip:
```python
pip install bulstem
```

The DeepL Translation API: https://www.deepl.com/docs-api/translate-text

## How to run it

* You should create a DeepL account and use your Authentication Key for DeepL API.
```bash 
export DEEPL_AUTH_KEY=<YOUR_DEEPL_AUTH_KEY>
```

* Run the flask_ui.py script in order to start the UI:
```bash
python3 flask_ui.py
```

* Open http://127.0.0.1:5000 to access it.

## Example

<img width="1539" alt="Example" src="https://github.com/yonitoo/Enhanced-BG-gastronomy-translator/assets/36246462/2a6cda30-b7c2-42ff-8525-2677b8145f95">

## Inspiration

The way I came up with this project is due to my attendance on the RANLP'23 Conference, held in Varna, Bulgaria.
There was one poster paper there which intrigued me:

[!Translate: When You Cannot Cook Up a Translation, Explain](https://aclanthology.org/2023.ranlp-1.44) (Garcea et al., RANLP 2023)

They create a more complex solution for Italian gastronomy. 
Inspired by them, I decided to create an alternative for the Bulgarian gastronomy.

## Where would I submit it

This is a university project for the NLP course that is part of my Master's degree in FMI@Sofia University.
