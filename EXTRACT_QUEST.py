import fitz  # PyMuPDF
import re

def extract_questions(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        extracted_text = []

        for page_number in range(1, len(pdf_document) - 1):
            page = pdf_document[page_number]

            page_rect = page.rect
            limited_area_rect = fitz.Rect(
                page_rect.x0,  # Lado esquerdo
                page_rect.y0 + 75,  # Excluir os primeiros 40px (cabeçalho)
                page_rect.x1,  # Lado direito
                page_rect.y1 - 40  # Excluir os últimos 40px (rodapé)
            )
            text = page.get_text("text", clip=limited_area_rect)
            extracted_text.append(text)

        pdf_document.close()

        full_text = "\n".join(extracted_text)

        full_text = re.sub(r"\*\*.*?\*\*", "", full_text, flags=re.DOTALL)

        # Regex para capturar apenas os blocos que seguem o padrão "QUESTÃO <número>"
        question_pattern = r"(QUESTÃO \d+\s+.*?(?=QUESTÃO \d+|$))"
        questions = re.findall(question_pattern, full_text, re.DOTALL)

        # Limpar duplicatas nas alternativas
        cleaned_questions = []
        for question in questions:
            # Remover duplicatas das alternativas (ex: A, B, C...)
            question = re.sub(r"(\b[A-E]\b)\s+\1", r"\1", question)
            cleaned_questions.append(question.strip())

        return cleaned_questions
    except Exception as e:
        return [f"Erro ao processar o PDF: {e}"]

pdf_path = "pdf/prova2022_dia1.pdf"
questions = extract_questions(pdf_path)

with open("questoes.txt", "w", encoding="utf-8") as file:
    for question in questions:
        file.write(question + "\n\n")

print("Questões extraídas com sucesso!")
