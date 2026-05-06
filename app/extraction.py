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
    
prompt = f""" Read {full_pdf} and extract the important information in this document in JSON format:
Return ONLY valid JSON.
No text before or after.
No markdown.
No comments.
No explanations.
No code fences.
No invented fields.
All keys must be strings.
All values must be strings, numbers, booleans, or arrays.
"""

response = ollama.chat(
    model='phi3:mini',
    messages=[{'role': 'user', 'content': prompt}]
)


text_response = response["message"]["content"]

raw_text = text_response.replace("```json", "").replace("```", "").strip()

print(raw_text)
json_response = json.loads(raw_text)


print(json_response)

with open('output.json', 'w') as f:
    json.dump(json_response, f, indent=4)