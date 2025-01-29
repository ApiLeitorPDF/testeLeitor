import fitz  # PyMuPDF

def extract_questions_with_structure(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        estrutura_prova = []

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

            questao_atual = None
            coletando_comando = False
            coletando_enunciado = False
            ultima_letra = None  # Para armazenar a última letra de alternativa encontrada

            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            texto = span["text"].strip()
                            fonte = span["font"]
                            tamanho = span["size"]

                            # Identificar "QUESTÃO X" (Arial-BoldMT)
                            if fonte == "Arial-BoldMT" and texto.startswith("QUESTÃO"):
                                if questao_atual:  # Finaliza a questão anterior
                                    estrutura_prova.append(questao_atual)

                                questao_atual = {
                                    "numero": texto,
                                    "comando": "",
                                    "fonte": "",
                                    "enunciado": "",
                                    "alternativas": []
                                }
                                coletando_comando = True
                                ultima_letra = None

                            # Identificar "FONTE" (menor tamanho, 6.0)
                            elif tamanho == 6.0 and fonte == "ArialMT":
                                if questao_atual:
                                    questao_atual["fonte"] += texto  # Coleta a fonte inicial
                                    coletando_comando = False
                                    coletando_enunciado = True

                            # Adicionar linhas adicionais como parte da fonte
                            elif questao_atual and coletando_enunciado and tamanho == 6.0:
                                questao_atual["fonte"] += " " + texto

                            # Identificar alternativas (A, B, C, D, E)
                            elif texto in "ABCDE" and len(texto) == 1:
                                ultima_letra = texto

                            # Continua texto das alternativas
                            elif fonte == "ArialMT" and ultima_letra:
                                if questao_atual:
                                    if not questao_atual["alternativas"] or questao_atual["alternativas"][-1]["letra"] != ultima_letra:
                                        questao_atual["alternativas"].append({
                                            "letra": ultima_letra,
                                            "texto": texto
                                        })
                                    else:
                                        # Adiciona texto à alternativa existente
                                        questao_atual["alternativas"][-1]["texto"] += " " + texto
                                    coletando_enunciado = False

                            # Coletar o enunciado após a fonte
                            elif coletando_enunciado and fonte == "ArialMT":
                                questao_atual["enunciado"] += " " + texto

                            # Coletar trechos em itálico
                            elif coletando_enunciado and "Italic" in fonte:
                                if questao_atual:
                                    questao_atual["enunciado"] += " *" + texto + "*"  # Marca o texto itálico com asteriscos

                            # Coletar o comando da questão
                            elif questao_atual and coletando_comando:
                                questao_atual["comando"] += " " + texto

            # Adiciona a última questão da página
            if questao_atual:
                estrutura_prova.append(questao_atual)

        pdf_document.close()
        return estrutura_prova
    except Exception as e:
        return [f"Erro ao processar o PDF: {e}"]

def save_to_txt(output_txt_path, estrutura_prova):
    try:
        with open(output_txt_path, "w", encoding="utf-8") as file:
            for questao in estrutura_prova:
                file.write(f"{questao['numero']}\n\n")
                file.write(f"Comando:\n{questao['comando']}\n\n")
                file.write(f"Enunciado:\n{questao['enunciado']}\n\n")
                for alternativa in questao["alternativas"]:
                    file.write(f"{alternativa['letra']}) {alternativa['texto']}\n")
                file.write(f"\nFonte: {questao['fonte']}\n")
                file.write("\n" + "=" * 80 + "\n\n")
        print(f"Questões salvas em: {output_txt_path}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo TXT: {e}")

# Caminhos para entrada e saída
pdf_path = "pdf/prova2011_dia1.pdf"
output_txt_path = "questoes_extraidas_formatadas.txt"

# Processar e salvar as questões
estrutura_prova = extract_questions_with_structure(pdf_path)
save_to_txt(output_txt_path, estrutura_prova)
