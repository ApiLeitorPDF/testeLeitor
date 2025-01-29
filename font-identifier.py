import fitz

doc = fitz.open("pdf/prova2009_dia1-com-borda.pdf")
pagina = doc[1]

# Extrair blocos de texto com detalhes
blocos = pagina.get_text("dict")["blocks"]
for bloco in blocos:
    if "lines" in bloco:
        for linha in bloco["lines"]:
            for span in linha["spans"]:
                fonte = span["font"]
                tamanho = span["size"]
                print(f"Texto: {span['text']}\nFonte: {fonte}\nTamanho: {tamanho}\n---")
