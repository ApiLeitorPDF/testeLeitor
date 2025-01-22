import fitz

def extract_text_with_encoding_skip_pages(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        extracted_text = []

        # Iterar sobre as páginas, pulando a primeira e a última
        for page_number in range(1, len(pdf_document) - 1):
            page = pdf_document[page_number]
            # Extrair o texto no modo "text", que geralmente preserva a formatação
            text = page.get_text("text")
            # Tratar possíveis problemas de codificação
            text = text.encode('utf-8', errors='replace').decode('utf-8')
            extracted_text.append(text)

        pdf_document.close()
        return "\n".join(extracted_text)
    except Exception as e:
        return f"Erro ao processar o PDF: {e}"


pdf_path = "pdf/prova2024_dia2.pdf"

text = extract_text_with_encoding_skip_pages(pdf_path)

with open("texto_extraido_sem_primeira_e_ultima.txt", "w", encoding="utf-8") as file:
    file.write(text)

print("Texto extraído!")
