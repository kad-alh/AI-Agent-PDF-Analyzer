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


    if state["bullets"] is None:
        action = "extract_bullets"
    elif state["json_text"] is None:
        action = "format_json"    
    else:
        action = "repair_json"
    

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
          Convert the following bullet points into a single JSON object.

            RULES:
            - Output ONLY valid JSON.
            - Use double quotes.
            - Do not add or remove information.
            - Keep values exactly as written.
            - If something is missing, leave it null.

            BULLETS:
            {state["bullets"]}
            Return ONLY the JSON object.

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

          Fix the JSON so it becomes valid.

            RULES:
            - Output ONLY valid JSON.
            - Use double quotes.
            - Do not add or remove keys.
            - Do not change values unless required to fix JSON.
            - No explanations.

            BROKEN JSON:
            {state["json_text"]}
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