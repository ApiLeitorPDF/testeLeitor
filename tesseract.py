import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os

# Configurar o caminho do Tesseract, se necessário (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path, output_dir="output_images"):
    """
    Extrai texto de um PDF escaneado.

    Args:
        pdf_path (str): Caminho para o arquivo PDF.
        output_dir (str): Diretório para salvar imagens intermediárias (opcional).

    Returns:
        str: Texto extraído do PDF.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    text = ""
    doc = fitz.open(pdf_path)

    for page_number in range(len(doc)):
        # Extrair a página como imagem
        page = doc[page_number]
        pix = page.get_pixmap()
        image_path = os.path.join(output_dir, f"page_{page_number + 1}.png")
        pix.save(image_path)

        # Realizar OCR na imagem
        image = Image.open(image_path)
        page_text = pytesseract.image_to_string(image, lang="por")  # Para português, use "por"
        text += f"\n--- Página {page_number + 1} ---\n"
        text += page_text

    return text

def extract_images_from_pdf(pdf_path, output_dir="extracted_images"):
    """
    Extrai todas as imagens incorporadas de um PDF.

    Args:
        pdf_path (str): Caminho para o arquivo PDF.
        output_dir (str): Diretório para salvar imagens extraídas.

    Returns:
        None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)

    for page_number in range(len(doc)):
        page = doc[page_number]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]  # Referência da imagem no PDF
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # Extensão da imagem
            image_filename = os.path.join(
                output_dir, f"page_{page_number + 1}_image_{img_index + 1}.{image_ext}"
            )
            # Salvar a imagem no disco
            with open(image_filename, "wb") as image_file:
                image_file.write(image_bytes)

    print(f"Imagens extraídas e salvas em '{output_dir}'.")


# Exemplo de uso
pdf_file = "pdf/2021super.pdf"

# Extrair texto do PDF
output_text = extract_text_from_pdf(pdf_file)

# Salvar o texto extraído em um arquivo
with open("output_text.txt", "w", encoding="utf-8") as f:
    f.write(output_text)

print("Texto extraído e salvo em 'output_text.txt'.")

# Extrair imagens do PDF
extract_images_from_pdf(pdf_file)
