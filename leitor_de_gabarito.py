import fitz  # PyMuPDF
import re


def extrair_verticalmente_pymupdf(pdf_path, numero_pagina, lado="esquerdo"):
    doc = fitz.open(pdf_path)
    pagina = doc[numero_pagina]

    largura, altura = pagina.rect.width, pagina.rect.height

    y_offset_top = 150
    y_offset_bottom = 50

    if lado == "esquerdo":
        area = fitz.Rect(0, y_offset_top, largura / 2, altura - y_offset_bottom)
    elif lado == "direito":
        area = fitz.Rect(largura / 2, y_offset_top, largura, altura - y_offset_bottom)
    else:
        raise ValueError("Escolha 'esquerdo' ou 'direito' para o lado.")

    # Extrai o texto apenas na área definida
    texto = pagina.get_text("text", clip=area)

    # Filtra o texto para manter apenas questões e respostas
    texto_filtrado = filtrar_gabarito(texto)

    return texto_filtrado

def filtrar_gabarito(texto):
    # Expressão regular para capturar "QUESTÃO RESPOSTA" ou apenas "QUESTÃO" sem resposta
    padrao = re.compile(r"(\d{1,3})\s*(Anulado|[A-E]|[*]|\s*)")
    questoes = padrao.findall(texto)

    resultado = []
    for questao, resposta in questoes:
        resposta = resposta.strip()
        if not resposta or resposta == "*":
            resposta = "Anulada"
        resultado.append(f"{questao} {resposta}")

    return "\n".join(resultado)

def extrair_todas_paginas_pymupdf(pdf_path):
    # Abre o PDF
    doc = fitz.open(pdf_path)
    texto_completo = {"esquerdo": [], "direito": []}

    # Itera sobre as páginas do PDF
    for numero_pagina in range(len(doc)):
        texto_esquerdo = extrair_verticalmente_pymupdf(pdf_path, numero_pagina, lado="esquerdo")
        texto_direito = extrair_verticalmente_pymupdf(pdf_path, numero_pagina, lado="direito")
        texto_completo["esquerdo"].append(texto_esquerdo)
        texto_completo["direito"].append(texto_direito)

    return texto_completo


# Caminho para o PDF
pdf_path = f"pdf/gabarito2019.pdf"

try:
    # Extrai texto de todas as páginas do PDF
    texto_todas_paginas = extrair_todas_paginas_pymupdf(pdf_path)

    # Exibe os resultados para o PDF atual
    for j, (texto_esq, texto_dir) in enumerate(zip(texto_todas_paginas["esquerdo"], texto_todas_paginas["direito"])):
        print(texto_esq)
        print(texto_dir)
except Exception as e:
    print(f"Erro ao processar {pdf_path}: {e}")
