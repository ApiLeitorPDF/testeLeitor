import tkinter as tk
from tkinter import filedialog, scrolledtext, simpledialog, messagebox
import fitz  # PyMuPDF
import json
import re


def segmentar_questoes_enem(pdf_path):
    doc = fitz.open(pdf_path)
    questoes = []
    questao_atual = None
    alternativa_atual = None  # Armazena a letra da alternativa em processamento

    # Percorre as páginas (ajustando o range conforme necessário)
    for page in range(1, len(doc) - 1):
        page_obj = doc.load_page(page)
        # Se o texto completo da página começar com "INSTRUÇÕES PARA A REDAÇÃO", ignora a página
        page_text = page_obj.get_text()
        if page_text.strip().startswith("INSTRUÇÕES PARA A REDAÇÃO"):
            continue

        blocks = page_obj.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            # Se o bloco for uma imagem (tipo 1), insere o placeholder
            if block.get("type") == 1:
                placeholder = "[aqui tem imagem]"
                # Debug: imprimir se um bloco de imagem foi encontrado
                # print("Bloco de imagem encontrado na página", page)
                if questao_atual:
                    if alternativa_atual:  # Se estiver processando uma alternativa
                        questao_atual["alternativas"][alternativa_atual] = questao_atual["alternativas"].get(alternativa_atual, "") + " " + placeholder
                    else:  # Caso contrário, adiciona ao enunciado da questão
                        questao_atual["enunciado"] += " " + placeholder
                continue

            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    tamanho = span["size"]
                    texto = span["text"].strip()
                    # Remove tabulações e \u0007, se necessário (ou substitua por espaço)
                    texto = re.sub(r'[\t\u0007]+', ' ', texto)
                    fonte = span["font"]

                    # Ignora spans com tamanho indesejado ou textos que correspondam a cabeçalhos de seção indesejados
                    if (fonte == "Arial-BoldMT" and tamanho == 8) or tamanho < 5 or tamanho > 11 or \
                        any(texto.startswith(s) for s in [
                            "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS Questões de 01 a 45",
                            "CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS Questões de 46 a 90",
                            "CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS Questões de 91 a 135",
                            "MATEMÁTICA E SUAS TECNOLOGIAS Questões de 136 a 180",
                            "Questões de 01 a 05 (opção espanhol)",
                            "19 CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS",
                            "Questões de 46 a 90",
                            "CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS",
                            "• LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS E REDAÇÃO • 1",
                            "DIA • CADERNO 1 • AZUL 5",
                            "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS E REDAÇÃO",
                            "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS E REDAÇÃO • 1",
                            "DIA • CADERNO 1 • AZUL •",
                            "DIA • CADERNO 1 • AZUL ",
                            "DIA • CADERNO [1-3][0-9]",
                            "DIA • CADERNO [0-9]",
                            "DIA • CADERNO 1 • AZUL •",
                            "DIA • CADERNO 1 • AZUL r'^[0-9]$",
                            "DIA • CADERNO 1 • AZUL r'^[0-9][0-9]$",
                            "• CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS • 1",
                            "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS",
                            "Questões de 06 a 45",
                            "DIA •",
                            "DIA",
                            "\t\u0007 ",
                            "LC - 1º dia | Caderno "
                        ]):
                        continue

                    # Início de nova questão: detecta pela fonte Arial-BoldMT e texto que inicia com "QUESTÃO" ou "Questão"
                    if fonte == "Arial-BoldMT" and (texto.startswith("QUESTÃO") or texto.startswith("Questão")):
                        if questao_atual:
                            questoes.append(questao_atual)
                        questao_atual = {
                            "enunciado": texto,
                            "alternativas": {},
                            "alternativa_correta": ""
                        }
                        alternativa_atual = None

                    # Marcador de alternativa: detecta pela fonte BundesbahnPiStd-1 e texto de apenas uma letra (A a E)
                    elif fonte == "BundesbahnPiStd-1" and re.match(r'^[A-E]$', texto):
                        alternativa_atual = texto

                    # Se a fonte for uma das desejadas e houver um marcador ativo, acumula o texto da alternativa
                    elif fonte in ["ArialMT", "Arial-ItalicMT", "Arial-BoldMT"] and alternativa_atual is not None:
                        if questao_atual:
                            questao_atual["alternativas"][alternativa_atual] = questao_atual["alternativas"].get(alternativa_atual, "") + " " + texto
                    # Se a fonte for uma das desejadas sem marcador ativo, acumula no enunciado
                    elif fonte in ["ArialMT", "Arial-ItalicMT", "Arial-BoldMT"]:
                        if questao_atual:
                            questao_atual["enunciado"] += " " + texto
                        alternativa_atual = None
                    else:
                        alternativa_atual = None

    if questao_atual:
        questoes.append(questao_atual)
    return questoes


def process_pdf():
    pdf_path = filedialog.askopenfilename(title="Selecione o PDF da prova", filetypes=[("Arquivos PDF", "*.pdf")])
    if not pdf_path:
        return

    ano_prova = simpledialog.askinteger("Ano da Prova", "Digite o ano da prova:")
    if ano_prova is None:
        return
    dia_prova = simpledialog.askinteger("Dia da Prova", "Digite o dia da prova:")
    if dia_prova is None:
        return

    gab_dict = {}
    if dia_prova == 1:
        gab_path = filedialog.askopenfilename(title="Selecione o arquivo TXT do gabarito", filetypes=[("Arquivos TXT", "*.txt")])
        if gab_path:
            try:
                with open(gab_path, encoding="utf-8") as f:
                    gab_lines = f.readlines()
                for line in gab_lines:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        try:
                            qnum = int(parts[0])
                        except ValueError:
                            continue
                        resposta = parts[1].strip().upper()
                        if resposta in ["ANULADA", "*", "", "Anulada", "anulada"]:
                            gab_dict[qnum] = ""
                        else:
                            gab_dict[qnum] = resposta
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível ler o arquivo de gabarito:\n{e}")

    questoes_extraidas = segmentar_questoes_enem(pdf_path)

    # Associa a alternativa correta a cada questão (assumindo que as questões estão na ordem)
    for i, questao in enumerate(questoes_extraidas):
        num_questao = i + 1
        if num_questao <= 5:
            questao["alternativa_correta"] = gab_dict.get(num_questao, "")
        elif 6 <= num_questao <= 10:
            questao["alternativa_correta"] = ""
        else:
            questao["alternativa_correta"] = gab_dict.get(num_questao - 6, "")

    exam_data = {
        "prova": "ENEM",
        "ano": ano_prova,
        "questoes": questoes_extraidas
    }

    json_output = json.dumps(exam_data, ensure_ascii=False, indent=2)
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, json_output)


def save_json():
    output_path = filedialog.asksaveasfilename(title="Salvar JSON como", defaultextension=".json", filetypes=[("Arquivos JSON", "*.json")])
    if output_path:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json_file.write(text_box.get(1.0, tk.END))
        messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{output_path}")


def exit_app():
    root.quit()


# Configuração da interface gráfica
root = tk.Tk()
root.title("Conversor de PDF para JSON - ENEM")

# Adiciona um menu (se o ambiente permitir)
menu_bar = tk.Menu(root)
arquivo_menu = tk.Menu(menu_bar, tearoff=0)
arquivo_menu.add_command(label="Salvar", command=save_json)
arquivo_menu.add_separator()
arquivo_menu.add_command(label="Sair", command=exit_app)
menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
root.config(menu=menu_bar)

# Se o menu não for visível (por ambiente), adicionamos botões na interface
frame_buttons = tk.Frame(root, padx=5, pady=5)
frame_buttons.pack(fill=tk.X)

btn_process = tk.Button(frame_buttons, text="Selecionar PDF e Processar", command=process_pdf)
btn_process.pack(side=tk.LEFT, padx=5)

btn_save = tk.Button(frame_buttons, text="Salvar JSON", command=save_json)
btn_save.pack(side=tk.LEFT, padx=5)

btn_exit = tk.Button(frame_buttons, text="Sair", command=exit_app)
btn_exit.pack(side=tk.LEFT, padx=5)

# Editor de texto (scrolledtext) para exibir o JSON gerado
text_box = scrolledtext.ScrolledText(root, width=100, height=30)
text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
