import pdfplumber # Bringing in the pdfplumber library to have access to pdfs
import ollama 
import json

with pdfplumber.open("sample_agreements/agreement.pdf") as pdf: #Using pdfplumber.open() to open and read the pdf file
    
    x = pdf.pages[0] 
    y = pdf.pages[1]
    pdf1 = x.extract_text()
    pdf2 = y.extract_text()
    full_pdf = pdf1 + pdf2
    split_text = full_pdf.split()
    full_pdf = " ".join(full_pdf.split())
    

prompt = f"""
Read this rental agreement: {full_pdf} Return ONLY valid JSON.
These are the rules:
No comments
No trailing commas
No markdown
No explanations
Arrays must contain only values, not objects with no keys
Every object must be key:value
All strings must use double quotes
Do not invent fields
Do not wrap JSON in ```json fences"""

response = ollama.chat(
    model='phi3:mini',
    messages=[{'role': 'user', 'content': prompt}]
)


text_response = response["message"]["content"]

raw_text = text_response.replace("```json", "").replace("```", "").strip()


json_response = json.loads(text_response)


print(json_response)

with open('output.json', 'w') as f:
    json.dump(json_response, f, indent=4)