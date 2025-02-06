import requests
from bs4 import BeautifulSoup


def coletar_questao(url, numero_questao):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        div_principal = soup.find('div', class_='elementor-element-cf8b365')

        if not div_principal:
            print(f"Div principal não encontrada na página {url}")
            return f"Questão {numero_questao} anulada."

        titulo_questao = div_principal.find('p', class_='has-text-align-center')
        texto_questao = div_principal.find_all('p')

        alternativas = []
        resposta_certa = ""
        for p in texto_questao:
            if p.text and p.text.strip().startswith(('A)', 'B)', 'C)', 'D)', 'E)')):
                alternativas.append(p.text.strip())
                if "(Alternativa" in p.text:
                    resposta_certa = p.text.split("(Alternativa ")[-1].strip().strip(")")

        solucao = div_principal.find('strong', string="Solução")
        explicacao = solucao.find_next('p') if solucao else None

        referencia = div_principal.find('p', class_='has-small-font-size')
        referencia_texto = referencia.text.strip() if referencia else "Referência não encontrada"

        return {
            'titulo': titulo_questao.text if titulo_questao else 'Título não encontrado',
            'texto': [p.text for p in texto_questao if p.text.strip() != ''],
            'alternativas': alternativas,
            'solucao': (
                           explicacao.text.strip() if explicacao else 'Solução não encontrada') + f"\nResposta correta: {resposta_certa}",
            'referencia': referencia_texto
        }
    else:
        print(f"Erro ao acessar a página {url}")
        return f"Questão {numero_questao} anulada."


questoes = []

for i in range(10, 92):
    url_completa = f"https://xequematenem.com.br/blog/questao-{i}-enem-2021/"
    print(f"Coletando: {url_completa}")
    questao = coletar_questao(url_completa, i)
    questoes.append(questao)

# Salvando as questões em um arquivo .txt
with open("questoes_enemd_2021.txt", "w", encoding="utf-8") as file:
    for i, questao in enumerate(questoes, start=10):
        if isinstance(questao, str):
            file.write(f"\n{questao}\n")
        else:
            file.write(f"<p>\nQuestão {i}:<p>\n")
            file.write(f"<p>Título: {questao['titulo']}</p>\n")
            file.write(f"<p>Enunciado: {' '.join(questao['texto'])}<p>\n")
            file.write("Alternativas:\n")
            for alternativa in questao['alternativas']:
                file.write(f"<p>  {alternativa}<p>\n")
            file.write(f"Solução: {questao['solucao']}\n")
            file.write(f"Referência: {questao['referencia']}\n")
            file.write("\n" + "-" * 50 + "\n")

print("Coleta concluída e salva no arquivo 'questoes_enemd_2021.txt'.")
