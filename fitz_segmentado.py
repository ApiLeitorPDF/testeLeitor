import fitz

def segmentar_questoes_enem(pdf_path):
    doc = fitz.open(pdf_path)
    estrutura_prova = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        
        questao_atual = None
        coletando_comando = False
        coletando_enunciado = False
        tamanho_padrao = 9.75  # Tamanho base do texto normal
        ultima_letra = None  # Para armazenar a última letra de alternativa encontrada
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        texto = span["text"].strip()
                        fonte = span["font"]
                        tamanho = span["size"]
                        
                        # Identificar QUESTÃO X (Arial-BoldMT)
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
                            
                        # Identificar FONTE (menor tamanho, 6.0)
                        elif tamanho == 6.0 and fonte == "ArialMT":
                            if questao_atual:
                                questao_atual["fonte"] = texto
                                coletando_comando = False
                                coletando_enunciado = True
                            
                        # Identificar alternativas (A) B) C) D) E)
                        elif fonte == "BundesbahnPiStd-1" and texto in 'ABCDE':
                            ultima_letra = texto
                        
                        # Continuação do texto das alternativas em ArialMT
                        elif fonte == "ArialMT" and ultima_letra:
                            if questao_atual:
                                # Se ainda não há alternativas ou a última alternativa não foi adicionada
                                if not questao_atual["alternativas"] or questao_atual["alternativas"][-1]["letra"] != ultima_letra:
                                    questao_atual["alternativas"].append({
                                        "letra": ultima_letra,
                                        "texto": texto
                                    })
                                else:
                                    # Adiciona o texto à alternativa já existente
                                    questao_atual["alternativas"][-1]["texto"] += " " + texto
                                ultima_letra = None  # Limpa a última letra
                                coletando_enunciado = False
                        
                        # Coletar o enunciado que vem após a fonte
                        elif coletando_enunciado and fonte == "ArialMT":
                            questao_atual["enunciado"] += " " + texto
                        
                        # Coletar outros componentes do comando
                        else:
                            if questao_atual and coletando_comando:
                                questao_atual["comando"] += " " + texto
                                    
        # Adiciona a última questão da página
        if questao_atual:
            estrutura_prova.append(questao_atual)
            
    return estrutura_prova

# Uso no Colab

# Upload do PDF
pdf_path = "pdf/prova2009_dia1.pdf"

# Processar e exibir
prova_estruturada = segmentar_questoes_enem(pdf_path)

# Exemplo de saída formatada
for i, questao in enumerate(prova_estruturada[:10]):  # Mostra as 3 primeiras
    print(f"\n{questao['numero']}")
    print(f"Comando: {questao['comando'].strip()}")
    print(f"Fonte: {questao['fonte']}")
    print(f"Enunciado: {questao['enunciado'].strip()}")
    print("Alternativas:")
    for alt in questao['alternativas']:
        print(f"- {alt['letra']}) {alt['texto']}")
    print("\n" + "-"*50)
