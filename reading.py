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
    pdf_path = "pdf/gabaritodia22024.pdf"

    try:
        result = process_pdf(pdf_path)
        print("Texto extraído:")
        #print(result["text"])
        contador = 0
        contador2 = 0
        gabarito = []

        # # Supondo que `result["text"]` seja o texto de onde as letras estão sendo extraídas
        for letras in result["text"]:
        #     contador2 += 1
        #     if contador2 > 161:  # Ignorar as primeiras 161 letras
            gabarito.append(letras)
            print(letras, end="")

        # Converter o gabarito extraído em um formato processável
        texto = ''.join(gabarito)  # Juntar todas as letras
        linhas = texto.split("\n")  # Dividir por linhas
        gabarito_processado = []

        # Processar o texto extraído
        for linha in linhas:
            if linha.strip():  # Ignorar linhas vazias
                partes = linha.split()
                numero = int(partes[0])  # Número da questão
                alternativas = partes[1:]  # Alternativas
                gabarito_processado.append((numero, alternativas))

        gabarito_processado.sort(key=lambda x: x[0])

        resultado = []
        for i, (numero, alternativas) in enumerate(gabarito_processado):
            if i < 5:
                resultado.append(f"{numero} {' '.join(alternativas[:2])}")
            else:
                resultado.append(f"{numero} {alternativas[0]}")

        gabarito_ordenado = "\n".join(resultado)
        print("\nGabarito Final Ordenado:")
        print(gabarito_ordenado)



    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
