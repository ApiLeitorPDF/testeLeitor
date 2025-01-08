import os
import pdfplumber

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
    pdf_path = "pdf/superampli2017-5-6.pdf"

    try:
        result = process_pdf(pdf_path)
        print("Texto extraído:")
        print(result["text"])
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
