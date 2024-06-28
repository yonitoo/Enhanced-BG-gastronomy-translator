import json
from openai import OpenAI
from constants import OPENAI_API_KEY, OPENAI_MODEL

def refine_definitional_contexts(terms):
    client = OpenAI(api_key=OPENAI_API_KEY)
    instruction = (
        "You are a specialist in Machine translation. Your task is to extract definitional context for each term in a dictionary. \nAristotle formulated definitional contexts as sequences of type\n"
        "X = Y + C , where X is the definiendum (the term), = is the definitor (a connective verb such as ‘to be’ or ‘consist’), Y is the definiens (the genus phrase, or nearest superconcept), and C are the differentiæ specificæ, the distinguishing characteristics "
        "that specify the distinction between one definiendum and another. For example, the definitional context for gnudi is as follows:\n X (Gnudi) = Y (gnocchi-like dumplings) + C (made with ricotta cheese instead of potato).\n\n"
        "The provided content contains some generic gastronomical terms such as 'Българска кухня', 'Кюфтета с кашкавал' and so on. Therefore, you would have to remove some of the items that seem redundant (does not seem characteristic to the local cuisine). "
        "Also, some of the items might have to be modified slightly, such as 'Елена (филе)' to 'Филе Елена', 'Торта \"Гараш\"' to 'Торта Гараш', '\"Кебапче Кюфте Шишчета Пържола Наденичка КарначеСервира се\" на \"Кебапче, Кюфте, Шишчета, Пържола, Наденичка, Карначе. Сервира се\"' and so on.\n"
        "Having this information, extract the definitional context from the following text using this formulation. Don't extract anything more but it should be in the form of sentences as it would be used as a translation helper, not X + Y = C. We also don't have to necessarily mention which country it comes from in the definitional context - drop it if mentioned. "
        "I want the output to be in the format 'Title:...' and 'Content:...' for each item. The definitional context usually is the first two sentences that provide a clear definition or description of the main term:\n\n"
    ) 
    terms_list = [f"Title: {title}\nContent: {term_data['definitional_context']}" for title, term_data in terms.items()]
    combined_content = "\n\n".join(terms_list)
    prompt = f"{combined_content}\n\nRefined terms:"
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0
    )
    refined_response = response.choices[0].message.content.strip()
    refined_terms = {}
    for line in refined_response.split("\n"):
        print(line)
        if line.startswith("Title:"):
            current_title = line[len("Title:"):].strip()
            print(current_title)
        elif line.startswith("Content:") and current_title:
            if current_title in terms:
                refined_terms[current_title] = {
                    "definitional_context": line[len("Content:"):].strip(),
                    "transliteration": terms[current_title]["transliteration"]
                }

    return refined_terms


def main():
    input_file = 'Glossary_fr.json'
    output_file = 'Glossary_cleaned_fr.json'
    
    with open(input_file, 'r', encoding='utf-8') as file:
        terms = json.load(file)["terms"]

    print(len(terms))
    
    refined_terms = refine_definitional_contexts(terms)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({"terms": refined_terms}, file, ensure_ascii=False, indent=4)
    print(f"Refined terms have been saved to {output_file}.")


if __name__ == "__main__":
    main()
