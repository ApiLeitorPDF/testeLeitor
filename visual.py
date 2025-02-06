import tkinter as tk
from tkinter import filedialog, scrolledtext, simpledialog, messagebox
import fitz  # PyMuPDF
import json
import re
import base64  # Import necessário para converter imagens para base64

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
            # Se o bloco for do tipo imagem, processa e insere a tag HTML com a imagem em base64
            if block.get("type") == 1:
                xref = block.get("image")
                try:
                    img_info = doc.extract_image(xref)
                    img_bytes = img_info["image"]
                    ext = img_info["ext"]
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    html_img_tag = f'<img src="data:image/{ext};base64,{img_b64}" />'
                    # Se já estivermos processando uma questão, adiciona a imagem ao enunciado
                    if questao_atual:
                        questao_atual["enunciado"] += " " + html_img_tag
                except Exception as e:
                    print("Erro ao processar imagem:", e)
                continue

            # Processa apenas blocos que possuem linhas (ou seja, blocos de texto)
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    tamanho = span["size"]
                    texto = span["text"].strip()
                    texto = re.sub(r'[\t\u0007]+', '', texto)
                    fonte = span["font"]

                    # Ignora spans cujo tamanho não esteja entre 5 e 11, ou seja, se for menor que 5, maior que 11, ou igual a 7 ou 8
                    if tamanho < 5 or tamanho > 11 or tamanho in (7, 8) or \
                            texto.startswith("LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS Questões de 01 a 45") or \
                            texto.startswith("CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS Questões de 46 a 90") or \
                            texto.startswith("CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS Questões de 91 a 135") or \
                            texto.startswith("MATEMÁTICA E SUAS TECNOLOGIAS Questões de 136 a 180") or \
                            texto.startswith("Questões de 01 a 05 (opção espanhol)") or \
                            texto.startswith("19 CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS") or \
                            texto.startswith("Questões de 46 a 90") or \
                            texto.startswith("Questões de 06 a 45") or \
                            texto.startswith("CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS") or \
                            texto.startswith("LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS") or \
                            texto.startswith("\t\u0007 ") or \
                            texto == "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS Questões de 06 a 45" or \
                            texto.startswith("LC - 1º dia | Caderno "):
                        continue

                    # Início de nova questão: usa fonte Arial-BoldMT e texto que inicia com "QUESTÃO" ou "Questão"
                    if fonte == "Arial-BoldMT" and (texto.startswith("QUESTÃO") or texto.startswith("Questão")):
                        if questao_atual:
                            questoes.append(questao_atual)
                        questao_atual = {
                            "enunciado": texto,
                            "alternativas": {},
                            "alternativa_correta": ""
                        }
                        alternativa_atual = None

                    # Marcador de alternativa: fonte BundesbahnPiStd-1 e texto é apenas uma letra (A a E)
                    elif fonte == "BundesbahnPiStd-1" and re.match(r'^[A-E]$', texto):
                        alternativa_atual = texto

                    # Se a fonte for ArialMT, Arial-ItalicMT ou Arial-BoldMT e houver um marcador ativo,
                    # acumula o texto da alternativa
                    elif fonte in ["ArialMT", "Arial-ItalicMT", "Arial-BoldMT"] and alternativa_atual is not None:
                        if questao_atual:
                            if alternativa_atual in questao_atual["alternativas"]:
                                questao_atual["alternativas"][alternativa_atual] += " " + texto
                            else:
                                questao_atual["alternativas"][alternativa_atual] = texto
                        # Não reseta alternativa_atual para permitir a concatenação de spans subsequentes

                    # Se a fonte for uma das desejadas e não estivermos capturando alternativa,
                    # acumula o texto no enunciado
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
                        if resposta in ["ANULADA", "*", "", "Anulada", "anulado"]:
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
