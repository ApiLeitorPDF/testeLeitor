import json

def formatar_questoes_em_json(caminho_txt, caminho_json):
    with open(caminho_txt, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.readlines()

    questoes = []
    questao_atual = {}
    alternativa_atual = None  # Variável para rastrear a alternativa atual

    for linha in conteudo:
        linha = linha.strip()

        if linha.startswith("QUESTÃO"):
            # Finaliza a questão anterior
            if questao_atual:
                questoes.append(questao_atual)
                questao_atual = {}

            # Cria uma nova questão
            questao_atual["questao"] = int(linha.split()[1])
            questao_atual["texto"] = ""
            questao_atual["alternativas"] = {}
            alternativa_atual = None  # Reinicia a alternativa atual

        elif linha.startswith(("A\t", "B\t", "C\t", "D\t", "E\t")):
            # Processa uma nova alternativa
            alternativa_atual = linha[0]  # Identifica a letra da alternativa (A, B, C, D ou E)
            questao_atual["alternativas"][alternativa_atual] = linha[2:].strip()  # Inicializa a alternativa com o texto

        elif alternativa_atual:
            # Continua adicionando ao texto da alternativa atual
            questao_atual["alternativas"][alternativa_atual] += " " + linha

        else:
            # Adiciona ao texto da questão
            questao_atual["texto"] += " " + linha

    # Adiciona a última questão
    if questao_atual:
        questoes.append(questao_atual)

    # Salva em JSON
    with open(caminho_json, 'w', encoding='utf-8') as arquivo_json:
        json.dump(questoes, arquivo_json, indent=4, ensure_ascii=False)

    print(f"Questões formatadas em JSON salvas em {caminho_json}")


caminho_txt = "questoes.txt"
caminho_json = "questoes.json"

formatar_questoes_em_json(caminho_txt, caminho_json)
