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
You MUST follow these rules EXACTLY: 1. Read the following document text: 
{full_pdf} 2. Extract ONLY the information that actually exists in the document. 
Do NOT invent, guess, assume, or add fields. 
3. Return the information in a single JSON object. 
4. The JSON MUST follow these rules: - Return ONLY valid JSON. - No text before or after the JSON. 
- No markdown. - No comments. - No explanations. - No code fences. - All keys must be strings. 
- All values must be strings, numbers, booleans, or arrays. - No trailing commas. 
- No single quotes. - ONLY double quotes. - No null unless the document explicitly contains a missing value. 
- Do NOT include fields that are not present in the document. 
5. If the document does not contain a piece of information, OMIT that field entirely. 
Your entire output MUST be one valid JSON object and nothing else.
DO NOT LEAVE OUT ANY INFORMATION THAT IS PRESENT IN THE DOCUMENT AND KEEP IT CONSISTENT WITH THE DOCUMENT.
  

"""

response = ollama.chat(
    model='phi3:mini',
    messages=[{'role': 'user', 'content': prompt}]
)


text_response = response["message"]["content"]

raw_text = text_response.replace("```json", "").replace("```", "").strip()


json_response = json.loads(raw_text)


print(json_response)

with open('output.json', 'w') as f:
    json.dump(json_response, f, indent=4)