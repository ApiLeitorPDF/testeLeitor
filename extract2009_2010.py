import fitz
import re

def extract_questions_with_cleaning(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        extracted_text = []

        # Extrair texto completo de cada página
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            text = page.get_text("text")
            extracted_text.append(text)

        pdf_document.close()

        full_text = "\n".join(extracted_text)

        cleanup_patterns = [
            r"(?i)CN – \dº dia",
            r"(?i)CADERNO \d+ – [A-Z]+",
            r"(?i)PÁGINA \d+",
            r"(?i)ENEM \d{4}",
            r"\s*-\s*"
        ]
        for pattern in cleanup_patterns:
            full_text = re.sub(pattern, "", full_text)

        full_text = re.sub(r"(?i)(Questão)\s*\n?\s*(\d+)", r"QUESTÃO \2", full_text)

        # Extrair apenas as questões com o formato corrigido
        question_pattern = r"(QUESTÃO\s*\d+\s+.*?(?=QUESTÃO\s*\d+|$))"
        questions = re.findall(question_pattern, full_text, re.DOTALL)

        # Limpar duplicatas nas alternativas e ajustar formatação
        cleaned_questions = []
        for question in questions:
            # Formatar o título da questão (com dois dígitos)
            question = re.sub(r"(QUESTÃO)\s*(\d+)", lambda m: f"{m.group(1)} {int(m.group(2)):02d}", question)

            # Corrigir apenas o espaçamento entre as alternativas
            question = re.sub(
                r"(\b[A-E])(\s+)([^\n])",  # Detectar alternativa com espaçamento incorreto
                r"\1\t\3",                # Inserir tabulação entre a letra e o texto
                question
            )

            # Garantir que múltiplas linhas em branco sejam reduzidas (sem afetar o enunciado)
            question = re.sub(r"\n{3,}", "\n\n", question.strip())

            cleaned_questions.append(question)

        return cleaned_questions
    except Exception as e:
        return [f"Erro ao processar o PDF: {e}"]


def save_to_txt(output_txt_path, questions):
    with open(output_txt_path, "w", encoding="utf-8") as file:
        for question in questions:
            file.write(question + "\n\n")

pdf_path = "pdf/prova2009_dia1-1-5.pdf"
output_txt_path = "questoes_formatadas.txt"

questions = extract_questions_with_cleaning(pdf_path)
save_to_txt(output_txt_path, questions)

print(f"QUESTÕES formatadas e limpas salvas em: {output_txt_path}")
