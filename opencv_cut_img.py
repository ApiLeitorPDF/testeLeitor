import cv2
import os
import random
import numpy as np

def process_images_in_directory(input_directory, output_directory):

    # Criar o diretório de saída se não existir
    os.makedirs(output_directory, exist_ok=True)

    # Listar todos os arquivos de imagem na pasta
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    input_images = [
        os.path.join(input_directory, f)
        for f in os.listdir(input_directory)
        if f.lower().endswith(image_extensions)
    ]

    # Processar cada imagem na lista
    for input_image_path in input_images:
        # Ler a imagem
        image = cv2.imread(input_image_path)
        if image is None:
            print(f"Não foi possível carregar a imagem: {input_image_path}")
            continue

        # Converter para escala de cinza com equalização de histograma
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # Suavizar a imagem para reduzir ruídos
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Aplicar Canny com thresholds dinâmicos
        median_val = np.median(blurred)
        lower_threshold = int(max(0, 0.7 * median_val))
        upper_threshold = int(min(255, 1.3 * median_val))
        edges = cv2.Canny(blurred, lower_threshold, upper_threshold)

        # Encontrar os contornos na imagem
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Inicializar contador de imagens extraídas
        image_counter = 0

        # Definir dimensões mínimas com base na imagem
        min_width = image.shape[1] * 0.15  # 15% da largura
        min_height = image.shape[0] * 0.15  # 15% da altura

        # Iterar sobre os contornos para encontrar e salvar as regiões que correspondem às imagens
        for contour in contours:
            # Obter o retângulo delimitador do contorno
            x, y, w, h = cv2.boundingRect(contour)

            # Filtrar contornos pequenos (dinâmico)
            if w > min_width and h > min_height:
                # Recortar a região da imagem
                cropped_image = image[y:y+h, x:x+w]

                # Salvar a imagem recortada
                base_name = os.path.splitext(os.path.basename(input_image_path))[0]
                output_path = os.path.join(output_directory, f'{base_name}_image_{image_counter}.png')
                cv2.imwrite(output_path, cropped_image)

                # Incrementar o contador
                image_counter += 1

# Exemplo de uso
def main():
    input_directory = './output_images'  # Diretório de entrada
    output_directory = './output_images-cut'  # Diretório de saída
    process_images_in_directory(input_directory, output_directory)

if __name__ == "__main__":
    main()
