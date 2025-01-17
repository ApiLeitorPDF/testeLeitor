import sys
import fitz  # PyMuPDF
import unicodedata
import re

sys.stdout.reconfigure(encoding="utf-8")

pdf_path = "pdf/2024ampli.pdf"

def normalizar_texto(texto):

    try:
        # Normaliza o texto para Unicode padrão
        texto_normalizado = unicodedata.normalize("NFKD", texto)
        # Remove ruídos, caracteres não imprimíveis e sequências repetidas
        texto_limpo = re.sub(r"[^\w\s.,;!?%()\-\"\'€$@áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ]", "", texto_normalizado)
        # Remove padrões específicos de cabeçalhos ou textos indesejados
        texto_limpo = re.sub(r"(ENEM\d{4})+", "ENEM", texto_limpo)
        texto_limpo = re.sub(r"(LC\s*[1Iil][ºoO0]?\s*DIA\s*CAD(?:ERNO)?(?:\s*\d+)?(?:\s*\w*)?)", "", texto_limpo, flags=re.IGNORECASE)
        texto_limpo = re.sub(r"(DERNO\s*\d+\s*\w+)", "", texto_limpo, flags=re.IGNORECASE)
        # Corrige espaçamentos excessivos e quebras de linha
        texto_limpo = re.sub(r"\s+", " ", texto_limpo).strip()
        return texto_limpo
    except Exception as e:
        print(f"Erro ao normalizar o texto: {e}")
        return texto

def extrair_verticalmente_pymupdf_completo(pdf_path, numero_pagina, lado="esquerdo"):

    doc = fitz.open(pdf_path)
    pagina = doc[numero_pagina]
    largura, altura = pagina.rect.width, pagina.rect.height

    if lado == "esquerdo":
        area = fitz.Rect(0, 0, largura / 2, altura)
    elif lado == "direito":
        area = fitz.Rect(largura / 2, 0, largura, altura)
    else:
        raise ValueError("Escolha 'esquerdo' ou 'direito' para o lado.")

    texto = pagina.get_text("text", clip=area)
    return normalizar_texto(texto)

def extrair_todas_paginas_pymupdf(pdf_path):

    doc = fitz.open(pdf_path)
    texto_completo = []

    for numero_pagina in range(1, len(doc)):  # Ignora a primeira página
        texto_esquerdo = extrair_verticalmente_pymupdf_completo(pdf_path, numero_pagina, lado="esquerdo")
        texto_direito = extrair_verticalmente_pymupdf_completo(pdf_path, numero_pagina, lado="direito")
        texto_concatenado = f"{texto_esquerdo}\n{texto_direito}"
        texto_completo.append(texto_concatenado)

    return texto_completo

def formatar_texto_questoes_ordenado(texto_completo):

    texto_questoes = []
    for pagina_texto in texto_completo:
        questoes = pagina_texto.split("QUESTÃO")
        questoes = [f"QUESTÃO {q.strip()}" for q in questoes if q.strip()]
        texto_questoes.extend(questoes)

    # Ordena as questões numericamente
    def extrair_numero(questao):
        match = re.search(r"\d+", questao)
        return int(match.group()) if match else float('inf')

    texto_questoes_ordenado = sorted(texto_questoes, key=extrair_numero)

    return "\n\n".join(texto_questoes_ordenado)

try:
    texto_todas_paginas = extrair_todas_paginas_pymupdf(pdf_path)
    texto_formatado = formatar_texto_questoes_ordenado(texto_todas_paginas)
    print(texto_formatado)
except Exception as e:
    print(f"Erro ao processar {pdf_path}: {e}")
