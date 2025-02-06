import fitz  # PyMuPDF
import json
import re

def segmentar_questoes_enem(pdf_path):
    doc = fitz.open(pdf_path)
    questoes = []
    questao_atual = None
    alternativa_atual = None  

    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    tamanho = span["size"]
                    if tamanho < 5 or tamanho > 11 or tamanho == 7 or tamanho == 8:
                        continue

                    texto = span["text"].strip()
                    fonte = span["font"]

                    # Início de nova questão: espera-se que a linha comece com "QUESTÃO" (usando Arial-BoldMT)
                    if fonte == "Arial-BoldMT" and texto.startswith("QUESTÃO"):
                        if questao_atual:
                            questoes.append(questao_atual)
                        questao_atual = {
                            "enunciado": texto,      # Contém o número e parte do enunciado
                            "alternativas": {},      # Alternativas serão um dicionário (ex: "A": "texto")
                            "alternativa_correta": ""  # Para preenchimento futuro
                        }
                        alternativa_atual = None

                    # Identifica marcador de alternativa: fonte "BundesbahnPiStd-1" e texto é apenas uma letra (A a E)
                    elif fonte == "BundesbahnPiStd-1" and re.match(r'^[A-E]$', texto):
                        alternativa_atual = texto

                    # Se a fonte for ArialMT ou Arial-ItalicMT e houver um marcador de alternativa ativo,
                    # trata o texto como parte do conteúdo da alternativa
                    elif fonte in ["ArialMT", "Arial-ItalicMT", "Arial-BoldMT"] and alternativa_atual is not None:
                        if questao_atual:
                            if alternativa_atual in questao_atual["alternativas"]:
                                questao_atual["alternativas"][alternativa_atual] += " " + texto
                            else:
                                questao_atual["alternativas"][alternativa_atual] = texto
                        # Não reseta alternativa_atual para poder capturar spans subsequentes

                    # Se a fonte for ArialMT ou Arial-ItalicMT e não estivermos capturando alternativa,
                    # considera o texto parte do enunciado
                    elif fonte in ["ArialMT", "Arial-ItalicMT", "Arial-BoldMT"]:
                        if questao_atual:
                            questao_atual["enunciado"] += " " + texto
                        alternativa_atual = None

                    else:
                        alternativa_atual = None

    if questao_atual:
        questoes.append(questao_atual)
    return questoes

# Caminho para o arquivo PDF (substitua pelo caminho correto)
pdf_path = "prova2024completa.pdf"

# Processa as questões e monta a estrutura final do JSON
questoes_extraidas = segmentar_questoes_enem(pdf_path)
exam_data = {
    "prova": "ENEM",
    "ano": 2019,
    "questoes": questoes_extraidas
}

json_output = json.dumps(exam_data, ensure_ascii=False, indent=2)
print(json_output)
