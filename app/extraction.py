import pdfplumber 
import ollama 
import json
import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection(name="pdf_chunks")

def chunk_text(text, max_length=1000):
    chunks = []
    collected_words = []
    split_words = text.split()

    for word in split_words:
        collected_words.append(word)
        current_list = " ".join(collected_words)   

        if len(current_list) >= max_length:
            chunks.append(current_list)            
            collected_words = []                   

    
    if collected_words:
        chunks.append(" ".join(collected_words))

    return chunks



opened_pdf = pdfplumber.open("sample_agreements/agreement.pdf") 
    
x = opened_pdf.pages[0] 
y = opened_pdf.pages[1]
pdf1 = x.extract_text()
pdf2 = y.extract_text()
full_pdf = pdf1 + pdf2
split_text = full_pdf.split()
full_pdf = " ".join(full_pdf.split())

chunked_bullets = ""
chunked_pdf = chunk_text(full_pdf, max_length = 1000)
for chunk in chunked_pdf: 
    respone = ollama.chat(
    model='mistral:latest',
    messages=[{'role': 'user', 'content': f"""
        Extract ONLY explicit facts from the following text.
        No summaries
        No combining facts
        No assumptions
        No rewriting
        One fact per bullet
        Use exact wording from the text

            TEXT:
            {chunk}

    Return ONLY bullet points

        """}]
        )
    
    bullet_list = respone["message"]["content"]
    chunked_bullets += bullet_list.strip() + "\n"
    
print("Extracted")


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
            model='mistral:latest',
            messages=[{'role': 'user', 'content': f"""
               Extract ONLY explicit facts from the document.
                - No summaries
                - No combining facts
                - No assumptions
                - No commentary
                - One fact per bullet
                - Use exact wording from the document

                DOCUMENT:

                {chunked_bullets}

                Return ONLY bullet points.

                """}]
                )
        bullets = response["message"]["content"]
        print("\nBullets extracted (preview):")
        print(bullets[:300], "...\n")
        state["bullets"] = bullets
    
    elif action == "format_json":
        response =  ollama.chat(
    model='mistral:latest',
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
    model='mistral:latest',
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

for i, chunk in enumerate(chunked_pdf):
    
    response = ollama.embeddings(
    model='nomic-embed-text:latest',
    prompt = chunk

    )
    embedding = response["embedding"]
    collection.add(
        ids=[f"chunk_{i}"],
        embeddings=[embedding], 
        documents=[chunk]

    )

print("All embeddings are now stored in ChromaDB")