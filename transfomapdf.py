import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os
import re
from pdf2image import convert_from_path


# Configurar o caminho do Tesseract, se necessário (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_as_pdf(pdf_path, output_pdf="output_text.pdf", output_dir="output_images"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    images = []
    for page_number in range(len(doc)):
        page = doc[page_number]
        pix = page.get_pixmap()
        image_path = os.path.join(output_dir, f"page_{page_number + 1}.png")
        pix.save(image_path)

        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Aplicar OCR e salvar a imagem com o texto embutido (opcional)
        text = pytesseract.image_to_string(image, lang="por")
        # print(f"Texto extraído da página {page_number + 1}:")
        print(text)
        images.append(image)

    if images:
        images[0].save(output_pdf, save_all=True, append_images=images[1:])
        print(f"PDF criado com as imagens OCR processadas em '{output_pdf}'.")
    else:
        print("Nenhuma imagem encontrada para salvar no PDF.")


def extract_text_from_image_pdf(file_path, crop_area=None):
    text = ""
    images = convert_from_path(file_path)
    for image in images:
        if crop_area:
            image = image.crop(crop_area)
        text += pytesseract.image_to_string(image, lang="por") + "\n"
    return text


def clean_text(text):
    text = re.sub(r"(ENEM2024|ENEM20E4|ENEM2024)+", "ENEM2024", text)
    text = re.sub(r"ENEM2024", "", text)
    text = re.sub(r"• LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS.*?\*011475AM[0-9]*\*", "", text)
    return text


def extract_from_question(text, start_phrase="QUESTÃO 01"):
    start_index = text.find(start_phrase)
    if start_index == -1:
        raise ValueError(f"A frase '{start_phrase}' não foi encontrada no texto.")
    return text[start_index:]


def process_pdf(file_path, crop_area=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")

    text = extract_text_from_image_pdf(file_path, crop_area)
    cleaned_text = clean_text(text)
    question_text = extract_from_question(cleaned_text)
    return {"text": question_text}


# Exemplo de uso
pdf_file = "pdf/2021super.pdf"

# Criar PDF com as imagens OCR processadas
extract_text_as_pdf(pdf_file, output_pdf="output_text_images.pdf")

try:
    result = process_pdf("output_text_images.pdf")
    print("Texto extraído a partir de 'QUESTÃO 01':")
    print(result["text"])
except Exception as e:
    print(f"Erro ao processar o PDF: {e}")
