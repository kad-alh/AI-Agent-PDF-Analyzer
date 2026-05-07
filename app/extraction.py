import pdfplumber # Bringing in the pdfplumber library to have access to pdfs
import ollama 
import json


opened_pdf =pdfplumber.open("sample_agreements/agreement.pdf") #Using pdfplumber.open() to open and read the pdf file
    
x = opened_pdf.pages[0] 
y = opened_pdf.pages[1]
pdf1 = x.extract_text()
pdf2 = y.extract_text()
full_pdf = pdf1 + pdf2
split_text = full_pdf.split()
full_pdf = " ".join(full_pdf.split())


response = ollama.chat(
    model='phi3:mini',
    messages=[{'role': 'user', 'content': f"""
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
  """}]
)


text_response = response["message"]["content"]

raw_text = text_response.replace("```json", "").replace("```", "").strip()



validation_response = ollama.chat(
    model='phi3:mini',
    messages=[{'role': 'user', 'content': f"""Go through the following information and ONLY check if it is valid JSON format, 
               DO NOT comment, add, remove, or do anything with this information, your job is to validate the JSON format, then if the format is not correct,
               you are allowed to FIX ONLY, and not to add anything from yourself, so that it can be valid to be used in json.loads().
                This is the text:{raw_text}""" }]
)


validated_response = validation_response["message"]["content"]


text_to_json = validated_response.replace("```json", "").replace("```", "").strip()
json_response = json.loads(text_to_json)

print(json_response)

with open('output.json', 'w') as f:
    json.dump(json_response, f, indent=4)