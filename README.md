# AI-Agent-PDF-Analyzer

This project extracts structured data from rental agreement PDFs using Python, pdfplumber, and a local LLM running through Ollama (Phi‑3). It converts unstructured contract text into clean JSON, capturing key details such as rent terms, dates, responsibilities, utilities, fees, and signatures.

## 🚀 Features
- Extracts text from PDF rental agreements
- Sends content to a local LLM (Phi‑3 via Ollama)
- Generates structured JSON summaries
- Cleans and parses malformed model output safely
- Saves final structured data to `outputs/extracted.json`

## 🧠 Tech Stack
- Python  
- pdfplumber  
- Ollama (Phi‑3 model)  
- JSON5 for robust parsing  

## 📂 How It Works
1. Load and extract text from a PDF using pdfplumber  
2. Clean and preprocess the extracted text  
3. Send the text to a local LLM with a strict JSON prompt  
4. Clean and parse the model’s output  
5. Save the structured JSON to disk  
