import os

def extract_pdf(file_path):
    import fitz # PyMuPDF
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

if __name__ == "__main__":
    file_path = "d:/Desktop/Desktop/数学建模/tc_project/Question.pdf"
    text = extract_pdf(file_path)
    with open("d:/Desktop/Desktop/数学建模/tc_project/document/Question.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Extracted Question.pdf")
