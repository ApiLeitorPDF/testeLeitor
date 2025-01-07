import os
from PIL import Image, UnidentifiedImageError
import fitz  # PyMuPDF

UPLOAD_FOLDER = 'uploads'

# Criar diretório de uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def extract_images_from_pdf(file_path):
    """Extrai imagens de um PDF."""
    images = []
    pdf = fitz.open(file_path)
    for page_number in range(len(pdf)):
        page = pdf[page_number]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]

            try:
                # Abrir imagem a partir dos bytes
                import io
                image = Image.open(io.BytesIO(image_bytes))

                # # Converter para RGB se necessário
                # if image.mode == "CMYK":
                #     image = image.convert("RGB")

                # Salvar a imagem no formato PNG
                image_name = f"page_{page_number + 1}_image_{img_index + 1}.png"
                image_path = os.path.join(UPLOAD_FOLDER, image_name)
                image.save(image_path)
                images.append(image_path)
            except UnidentifiedImageError:
                print(
                    f"Erro: não foi possível identificar a imagem na página {page_number + 1}, índice {img_index + 1}.")
            except Exception as e:
                print(f"Erro ao processar a imagem: {e}")
    return images


def process_pdf(file_path):
    """Processa o PDF para extrair apenas imagens."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")

    # Extrair apenas imagens
    images = extract_images_from_pdf(file_path)

    return images


if __name__ == '__main__':
    # Caminho do arquivo PDF
    pdf_path = "pdf/prova.pdf"

    try:
        images = process_pdf(pdf_path)
        print("Imagens extraídas:")
        for image_path in images:
            print(image_path)
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
