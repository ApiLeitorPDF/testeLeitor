import re


def processar_questoes(arquivo_entrada, arquivo_saida):
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    questoes = re.split(r'--------------------------------------------------', conteudo)

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("<html>\n<head>\n<title>Questões ENEM 2021</title>\n</head>\n<body>\n")

        for questao in questoes:
            if questao.strip():
                f.write("<section>\n")
                linhas = questao.strip().split('\n')
                for linha in linhas:
                    if re.match(r'^[a-e]\)', linha.strip().lower()):
                        f.write(f"<p>{linha.strip()}</p>\n")
                    elif "Resposta correta:" in linha:
                        f.write(f"<p><strong>{linha.strip()}</strong></p>\n")
                    else:
                        f.write(f"<p>{linha.strip()}</p>\n")
                f.write("</section>\n<hr>\n")

        f.write("</body>\n</html>")


# Executando a função
processar_questoes('questoes_enem_2021.txt', 'questoes_enem_2021.html')
print("Arquivo HTML gerado com sucesso: questoes_enem_2021.html")
