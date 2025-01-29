import fitz

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
            ultima_letra = None

            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        texto_linha = ""
                        fonte_atual = None
                        tamanho_atual = None

                        for span in line["spans"]:
                            texto_span = span["text"].strip()
                            fonte = span["font"]
                            tamanho = span["size"]

                            # Verifica se estamos em um novo contexto (fonte/tamanho diferente)
                            if fonte_atual and (fonte != fonte_atual or tamanho != tamanho_atual):
                                texto_linha += " "  # Espaço entre spans diferentes

                            texto_linha += f"*{texto_span}*" if fonte == "Arial-ItalicMT" else texto_span
                            fonte_atual, tamanho_atual = fonte, tamanho

                        texto_linha = texto_linha.strip()

                        # Detecta início de uma nova questão
                        if fonte_atual == "Arial-BoldMT" and texto_linha.startswith("QUESTÃO"):
                            if questao_atual:
                                estrutura_prova.append(questao_atual)

                            questao_atual = {
                                "numero": texto_linha,
                                "comando": "",
                                "fonte": "",
                                "enunciado": "",
                                "alternativas": []
                            }
                            coletando_comando = True
                            ultima_letra = None

                        # Detecta fonte da questão
                        elif tamanho_atual == 6.0 and fonte_atual == "ArialMT":
                            if questao_atual:
                                questao_atual["fonte"] = texto_linha
                                coletando_comando = False
                                coletando_enunciado = True

                        # Detecta letras de alternativas (A, B, C, D, E)
                        elif texto_linha in "ABCDE" and len(texto_linha) == 1:
                            ultima_letra = texto_linha

                        # Detecta textos das alternativas
                        elif fonte_atual in ["ArialMT", "Arial-ItalicMT"] and ultima_letra:
                            if questao_atual:
                                if not questao_atual["alternativas"] or questao_atual["alternativas"][-1]["letra"] != ultima_letra:
                                    questao_atual["alternativas"].append({
                                        "letra": ultima_letra,
                                        "texto": texto_linha
                                    })
                                else:
                                    questao_atual["alternativas"][-1]["texto"] += f" {texto_linha}"

                                coletando_enunciado = False

                        # Coleta enunciado da questão
                        elif coletando_enunciado and fonte_atual in ["ArialMT", "Arial-ItalicMT"]:
                            questao_atual["enunciado"] += f" {texto_linha}"

                        # Coleta comando da questão
                        elif questao_atual and coletando_comando and fonte_atual in ["ArialMT", "Arial-ItalicMT"]:
                            questao_atual["comando"] += f" {texto_linha}"

            if questao_atual:
                estrutura_prova.append(questao_atual)

        pdf_document.close()
        return estrutura_prova
    except Exception as e:
        return [f"Erro ao processar o PDF: {e}"]

def save_to_markdown(output_md_path, estrutura_prova):
    try:
        with open(output_md_path, "w", encoding="utf-8") as md_file:
            for questao in estrutura_prova:
                # Cabeçalho da questão
                md_file.write(f"## {questao['numero']}\n\n")

                # Seção de Comando
                if questao['comando'].strip():
                    md_file.write("**Comando:**\n\n")
                    md_file.write(f"{questao['comando'].strip()}\n\n")

                # Seção de Enunciado
                if questao['enunciado'].strip():
                    md_file.write("**Enunciado:**\n\n")
                    md_file.write(f"{questao['enunciado'].strip()}\n\n")

                # Alternativas
                if questao['alternativas']:
                    md_file.write("**Alternativas:**\n\n")
                    for alt in questao['alternativas']:
                        md_file.write(f"- **{alt['letra']}.** {alt['texto']}\n")
                    md_file.write("\n")

                # Fonte
                if questao['fonte'].strip():
                    md_file.write(f"*Fonte: {questao['fonte'].strip()}*\n")

                md_file.write("\n---\n\n")

        print(f"Arquivo Markdown salvo em: {output_md_path}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo Markdown: {e}")

# Configurações
pdf_path = "pdf/prova2023_dia1.pdf"
output_md_path = "prova_enem_estruturada.md"

# Processamento
estrutura = extract_questions_with_structure(pdf_path)
save_to_markdown(output_md_path, estrutura)
