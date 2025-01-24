import fitz
import re

def extract_questions(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        extracted_text = []

        for page_number in range(1, len(pdf_document) - 1):
            page = pdf_document[page_number]

            page_rect = page.rect
            limited_area_rect = fitz.Rect(
                page_rect.x0,
                page_rect.y0 + 75,
                page_rect.x1,
                page_rect.y1 - 40
            )
            text = page.get_text("text", clip=limited_area_rect)
            extracted_text.append(text)

        pdf_document.close()

        full_text = "\n".join(extracted_text)

        # Remover intervalos de questões como "Questões de <número> a <número>" e variações
        full_text = re.sub(r"(?i)Questões?\s+de\s+\d{2}\s+a\s+\d{2}", "", full_text)

        # Remover expressões como "Questões de 06 a 45", "Questões de 01 a 45", etc.
        full_text = re.sub(r"(?i)Questões?\s+de\s+\d{2}\s+a\s+\d{2}.*", "", full_text)

        # Remover cabeçalhos de áreas como "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS"
        full_text = re.sub(r"(?i)LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS", "", full_text)

        # Remover repetições de "ENEM <ano>" e padrões do tipo NEM<ano>
        full_text = re.sub(r"(ENEM \d{4}\s+){2,}", "", full_text)
        full_text = re.sub(r"(NEM\d{4})\1+", "", full_text)

        # Remover qualquer ocorrência repetitiva de "ENE" ou "ENEM" ou "NEM"
        full_text = re.sub(r"(ENE|ENEM|NEM)\s*\1+", "", full_text)

        # Remover o "ENE" isolado (evitar "ENE" por conta própria)
        full_text = re.sub(r"\bENE\b", "", full_text)

        # Remover a expressão "(opção: <idioma>)"
        full_text = re.sub(r"\(opção:\s*\w+\)", "", full_text)

        # Regex para capturar apenas os blocos que seguem o padrão "QUESTÃO <número> ou Questão <número>"
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

def save_to_pdf(output_pdf_path, questions):
    pdf_document = fitz.open()
    for question in questions:
        page = pdf_document.new_page()
        page.insert_text((10, 10), question, fontsize=10, fontname="helv")
    pdf_document.save(output_pdf_path)
    pdf_document.close()

pdf_path = "pdf/prova2011_dia1.pdf"
output_txt_path = "questoes.txt"
output_pdf_path = "questoes_extraidas.pdf"

questions = extract_questions(pdf_path)

with open(output_txt_path, "w", encoding="utf-8") as file:
    for question in questions:
        file.write(question + "\n\n")

save_to_pdf(output_pdf_path, questions)

print("Questões extraídas e salvas com sucesso!")
