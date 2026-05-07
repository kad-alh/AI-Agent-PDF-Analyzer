import pdfplumber 
import ollama 
import json

opened_pdf = pdfplumber.open("sample_agreements/agreement.pdf") 
    
x = opened_pdf.pages[0] 
y = opened_pdf.pages[1]
pdf1 = x.extract_text()
pdf2 = y.extract_text()
full_pdf = pdf1 + pdf2
split_text = full_pdf.split()
full_pdf = " ".join(full_pdf.split())


state = {
    "bullets": None,
    "json_text": None,
    "valid": False
}

while not state["valid"]:

    print("Current state:")
    print("bullets is None:", state["bullets"] is None)
    print("json_text is None:", state["json_text"] is None)

    if state["bullets"] is None:
        action = "extract_bullets"
    elif state["json_text"] is None:
        action = "format_json"    
    else:
        action = "repair_json"
    print("Action:", action)

    if action == "extract_bullets":

        print("Extracting bullets from PDF...")

        response = ollama.chat(
            model='phi3:medium',
            messages=[{'role': 'user', 'content': f"""
               Extract ONLY explicit facts from the document.
                - No summaries
                - No combining facts
                - No assumptions
                - No commentary
                - One fact per bullet
                - Use exact wording from the document

                DOCUMENT:

                {full_pdf}

                Return ONLY bullet points.

                """}]
                )
        bullets = response["message"]["content"]
        print("\nBullets extracted (preview):")
        print(bullets[:300], "...\n")
        state["bullets"] = bullets
    
    elif action == "format_json":
        response =  ollama.chat(
    model='phi3:medium',
    messages=[{'role': 'user', 'content': f"""
            Convert the bullet points below into ONE valid JSON object.
            BULLET POINTS:
            {state["bullets"]}

            RULES:
            - Each bullet point becomes a key-value pair.
            - If a bullet point has no value, set the value to "".
            - Use ONLY double quotes.
            - No trailing commas.
            - No comments or explanations.
            - Output ONLY the JSON.

            """ }]
            )
        json_text = response["message"]["content"]
        print("\nFormatted JSON (preview):")
        print(json_text[:300], "...\n")
        state["json_text"] = json_text
        
        
    elif action == "repair_json":


        print("Repairing JSON...")
        response = ollama.chat(
    model='phi3:medium',
    messages=[{'role': 'user', 'content': f"""You will be given JSON that is invalid. Your job is to FIX it.

            RULES (follow EXACTLY):
            - Output ONLY valid JSON.
            - No explanations.
            - No comments.
            - No markdown.
            - No backticks.
            - No text before or after the JSON.
            - Use ONLY double quotes.
            - Do NOT invent or remove keys.
            - Do NOT change values unless required to fix JSON.
            - Do NOT add ellipses (...).
            - Do NOT truncate anything.
            - Do NOT reformat into multiple objects. Keep ONE object.

            Here is the JSON to fix:
            {state["json_text"]}

            Return ONLY the corrected JSON.

            """ }]

        )
        repaired_json = response["message"]["content"]
        print("\nRepaired JSON (preview):")
        print(repaired_json[:300], "...\n")
        state["json_text"] = repaired_json
        
    if state["json_text"] is not None:
        print("Validating JSON...")
        try:
            json.loads(state["json_text"])
            state["valid"] = True
        except:
            state["valid"] = False
    

final_json = json.loads(state["json_text"])

with open('output.json', 'w') as f:
    json.dump(final_json, f, indent=4)

print(f"Completed JSON: {final_json}")