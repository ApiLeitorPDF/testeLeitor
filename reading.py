import os
import pdfplumber
from pymupdf.extra import page_count


def extract_text_from_pdf(file_path):
    """Extrai texto de um PDF."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def process_pdf(file_path):
    """Processa o PDF para extrair texto."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")

    # Extrair apenas o texto
    text = extract_text_from_pdf(file_path)
    return {"text": text}



if __name__ == '__main__':
    # Caminho do arquivo PDF
    pdf_path = "pdf/gabaritodia22024.pdf"

    try:
        result = process_pdf(pdf_path)
        print("Texto extraído:")
        #print(result["text"])

        # Extrair apenas o texto
        with pdfplumber.open("pdf/2017gabarito.pdf") as pdf:
            page = pdf.pages[0]
            area_gabarito = (100, 220, 500, 780)
            cropped_page = page.within_bbox(area_gabarito)
            texto_area = cropped_page.extract_text()
            print(texto_area)



    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
