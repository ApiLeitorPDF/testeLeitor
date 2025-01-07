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
    pdf_path = "pdf/gabaritoenem.pdf"

    try:
        result = process_pdf(pdf_path)
        print("Texto extraído:")
        #print(result["text"])
        contador = 0
        contador2 = 0
        for letras in result["text"]:
            contador2 +=1
            if(contador2 > 161):
                print(letras, end='')

                contador += 1

            # if contador == 3:
            #     print()
            #     contador = 0



    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
