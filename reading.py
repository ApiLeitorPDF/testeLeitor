import os
import pdfplumber
import re


def extract_text_from_pdf(file_path, crop_area=None):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            # Skip the last page
            if i == total_pages - 1:
                continue

            page_width = page.width
            page_height = page.height

            top_percentage = 0.06 * page_height
            bottom_percentage = 0.06 * page_height

            crop_area = (0, top_percentage, page_width, page_height - bottom_percentage)

            if crop_area:
                cropped_page = page.within_bbox(crop_area)
                text += cropped_page.extract_text() + "\n"
            else:
                text += page.extract_text() + "\n"

    return text


def clean_text(text):
    text = re.sub(r"(ENEM2024|ENEM20E4|ENEM2024)+", "ENEM2024", text)
    text = re.sub(r"ENEM2024", "", text)
    text = re.sub(r"• LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS.*?\*011475AM[0-9]*\*", "", text)
    return text


def extract_from_question(text, start_phrase="QUESTÃO 01"):
    start_index = text.find(start_phrase)
    if start_index == -1:
        raise ValueError(f"A frase '{start_phrase}' não foi encontrada no texto.")
    return text[start_index:]


def process_pdf(file_path, crop_area=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")

    text = extract_text_from_pdf(file_path, crop_area)
    cleaned_text = clean_text(text)
    # Extrair a partir da "QUESTÃO 01"
    question_text = extract_from_question(cleaned_text)
    return {"text": question_text}


if __name__ == '__main__':
    pdf_path = "pdf/2018spamp.pdf"

    try:
        result = process_pdf(pdf_path)
        print("Texto extraído a partir de 'QUESTÃO 01':")
        print(result["text"])
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
