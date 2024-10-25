
def generate_prompt(text):
    prompt = f"""Extract relevant technologies/strategies and their details from the following ARTICLE:\n\n{text}\n\n

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
                    - Tables: Any tables present in the article [Use a dictionary to store the table number and the table content as a list of dictionaries]
                    - Figures: Any figures present in the article [Use a dictionary to store the figure number and the figure analysis as a list of dictionaries]
                    - Sources: Any sources present in the article [Use a dictionary to store the source number and the source content as a list of dictionaries]
                    
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
    return prompt