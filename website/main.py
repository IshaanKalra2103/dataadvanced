import json
import os
import re
import string
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import spacy
import nltk
from nltk.corpus import stopwords
from backend.website.prompt import generate_prompt



# Load environment variables from .env file
load_dotenv()

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Load NLTK stop words
stop_words = set(stopwords.words('english'))

# Load the article text from a PDF file
def load_article(file_path):
    reader = PdfReader(file_path)
    number_of_pages = len(reader.pages)
    text = ""

    for page_number in range(number_of_pages):
        page = reader.pages[page_number]
        text += page.extract_text()

    return text

# NLP Preprocessing: Remove stop words, punctuation, and perform lemmatization
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Process text using spaCy
    doc = nlp(text)

    # Lemmatize and remove stop words
    tokens = [token.lemma_ for token in doc if token.text not in stop_words and not token.is_punct]

    # Join tokens back into a single string
    processed_text = " ".join(tokens)
    
    return processed_text

def enhanced_extraction_with_llm(text):
    client = OpenAI(
        api_key=os.getenv('API_KEY')
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""Extract relevant technologies/strategies and their details from the following ARTICLE:\n\n{text}\n\n

                Based on these metrics:
                - Title: Title of the paper/abstract/report
                - Year
                - Lead author name
                - Keywords: List of keywords present in the article
                - Technologies/strategies:
                  - Name of the technology
                  - Reduction efficiency
                  - Applicability
                  - Value chain of technologies/strategies
                  - Types of technologies/strategies
                  - Cost of reduction
                - Countries: Specific countries mentioned in the paper
                - Notes: Any relevant notes (as an array of strings)

                Once data is collected, convert the data into the following JSON format(This is only an example with sample data):

                {{
                  "title": "Strategy Optimization and Technology Evaluation for Oil and Gas Methane Emission Detection",
                  "year": 2021,
                  "leadAuthorName": "R. Kou",
                  "keywords": ["methane emission", "oil and gas", "LDAR", "emission reduction"], --> (Be very extensive as to what keywords are mentioned in the article)
                  "technologiesStrategies": [
                    {{
                      "name": "OGI camera (annually)",
                      "reductionEfficiency": "24.3%",
                      "applicability": "All facilities",
                      "valueChain": "Gas production, oil production",
                      "type": "Upstream LDAR",
                      "costOfReduction": "Not specified"
                    }},
                    {{
                      "name": "Ground-based fixed sensor",
                      "reductionEfficiency": "39.1%",
                      "applicability": "Larger Areas",
                      "valueChain": "Gas production, oil production",
                      "type": "Upstream LDAR",
                      "costOfReduction": "Not specified"
                    }}
                  ],
                  "countries": ["China", "United States"],
                  "notes": [
                  "FEAST model simulates leak scenarios and tests LDAR strategies.",
                  "Ground-based fixed sensors achieved the highest reduction (39.1%).",
                  "OGI cameras followed with a 24.3% reduction.",
                  "Fixed-wing aerial surveys had a 6.8% reduction.",
                  "Increasing sensitivity and frequency improves performance.",
                  "Semi-annual OGI surveys and quarterly high-sensitivity aerial surveys yield notable reductions."
                  ]
                }}

                Please ensure that the JSON format is strictly followed, and provide only the JSON output.
                """
            }
        ],
        model="gpt-4o-mini",
    )

    return chat_completion.choices[0].message.content.strip()

def clean_json_string(json_string):
    # Remove any non-JSON characters (e.g., ```json and full stops)
    cleaned_string = re.sub(r'^```json\s*', '', json_string)  # Remove ```json at the beginning
    cleaned_string = re.sub(r'\s*```$', '', cleaned_string)    # Remove ``` at the end
    cleaned_string = cleaned_string.strip()  # Remove any leading/trailing whitespace
    return cleaned_string

def main(file_path):
    article_text = load_article(file_path)
    processed_text = preprocess_text(article_text)
    final_text = generate_prompt(str(processed_text)) #not working?
    print(final_text)
    enhanced_info = enhanced_extraction_with_llm(processed_text)

    # Clean JSON data
    cleaned_json_string = clean_json_string(enhanced_info)

    print("\nEnhanced Information with LLM:")
    print(cleaned_json_string)
    
    

    try:
        # Parse cleaned JSON string
        json_data = json.loads(cleaned_json_string)
        print("Parsed JSON Data:", json_data)  # Debug print
        # Instead of converting to CSV, just return the JSON data
        return json_data
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        print("Received JSON data:", cleaned_json_string)
        return {"error": "Error decoding JSON"}
