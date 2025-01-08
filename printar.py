import fitz  # PyMuPDF
from PIL import Image
import os


def pdf_to_images(pdf_path, output_dir="pdf_images", dpi=150):
    """
    Converte as páginas de um PDF em imagens e exibe cada uma.

    Args:
        pdf_path (str): Caminho para o arquivo PDF.
        output_dir (str): Diretório para salvar as imagens geradas.
        dpi (int): Resolução das imagens em DPI (padrão: 150).

    Returns:
        list: Lista de caminhos das imagens geradas.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_number in range(len(doc)):
        # Extrair a página como uma imagem rasterizada
        page = doc[page_number]
        pix = page.get_pixmap(dpi=dpi)
        image_path = os.path.join(output_dir, f"page_{page_number + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

        # Exibir a imagem usando PIL
        img.show(title=f"Página {page_number + 1}")

    print(f"Imagens salvas em '{output_dir}'.")
    return image_paths


# Exemplo de uso
pdf_file = "pdf/2024ampli.pdf"
pdf_to_images(pdf_file)
