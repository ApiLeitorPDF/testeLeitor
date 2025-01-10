import fitz  # PyMuPDF
import cv2
import os
import numpy as np
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_pages_as_images(pdf_path, output_dir="output_images"):
    """
    Extrai cada página de um PDF como imagem.

    Args:
        pdf_path (str): Caminho para o arquivo PDF.
        output_dir (str): Diretório para salvar as imagens das páginas.

    Returns:
        list: Lista de caminhos das imagens extraídas.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        pix = page.get_pixmap()
        image_path = os.path.join(output_dir, f"page_{page_number + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths

def process_and_cut_images(input_images, output_dir="cut-imgs"):
    """
    Processa uma lista de imagens, aplica transformações e recorta regiões de interesse.

    Args:
        input_images (list): Lista de caminhos para as imagens de entrada.
        output_dir (str): Diretório para salvar as imagens recortadas.

    Returns:
        None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_image_path in input_images:
        image = cv2.imread(input_image_path)
        if image is None:
            print(f"Não foi possível carregar a imagem: {input_image_path}")
            continue

        # Convertendo para o espaço de cor HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Definindo o intervalo de cor azul no espaço HSV
        lower_blue = np.array([100, 150, 50])  # Limite inferior da cor azul
        upper_blue = np.array([140, 255, 255])  # Limite superior da cor azul

        # Criando a máscara para detectar regiões azuis
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Aplicando a máscara na imagem original
        blue_region = cv2.bitwise_and(image, image, mask=mask)

        # Convertendo para escala de cinza para encontrar contornos
        gray = cv2.cvtColor(blue_region, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        median_val = np.median(blurred)
        lower_threshold = int(max(0, 0.7 * median_val))
        upper_threshold = int(min(255, 1.3 * median_val))
        edges = cv2.Canny(blurred, lower_threshold, upper_threshold)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_counter = 0
        min_width = image.shape[1] * 0.05
        min_height = image.shape[0] * 0.05

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            if w > min_width and h > min_height:
                cropped_image = image[y:y+h, x:x+w]

                base_name = os.path.splitext(os.path.basename(input_image_path))[0]
                output_path = os.path.join(output_dir, f'{base_name}_cut_{image_counter}.png')
                cv2.imwrite(output_path, cropped_image)

                image_counter += 1

    print(f"Imagens processadas e salvas em '{output_dir}'.")

def main():

    pdf_file = "pdf/2021super.pdf"  # Caminho do PDF de entrada
    cut_images_dir = "cut-imgs"
    page_images = extract_pages_as_images(pdf_file)
    process_and_cut_images(page_images, output_dir=cut_images_dir)

if __name__ == "__main__":
    main()
