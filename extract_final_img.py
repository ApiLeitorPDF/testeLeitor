import fitz
import cv2
import os
import numpy as np
import pytesseract
import shutil

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_pages_as_images(pdf_path, output_dir="output_images", scale_factor=3):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    image_paths = []

    mat = fitz.Matrix(scale_factor, scale_factor)

    for page_number in range(len(doc)):
        page = doc[page_number]
        pix = page.get_pixmap(matrix=mat)  # Apply scaling matrix
        image_path = os.path.join(output_dir, f"page_{page_number + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    doc.close()
    return image_paths

def process_and_cut_images(input_images, output_dir="cut-imgs"):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_image_path in input_images:
        image = cv2.imread(input_image_path)
        if image is None:
            print(f"Não foi possível carregar a imagem: {input_image_path}")
            continue

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_purple = np.array([125, 50, 50])
        upper_purple = np.array([160, 255, 255])

        mask = cv2.inRange(hsv, lower_purple, upper_purple)

        purple_region = cv2.bitwise_and(image, image, mask=mask)

        gray = cv2.cvtColor(purple_region, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        median_val = np.median(blurred)
        lower_threshold = int(max(0, 0.7 * median_val))
        upper_threshold = int(min(255, 1.3 * median_val))
        edges = cv2.Canny(blurred, lower_threshold, upper_threshold)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

        image_counter = 0
        min_width = image.shape[1] * 0.02
        min_height = image.shape[0] * 0.02

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            if w > min_width and h > min_height:
                cropped_image = image[y:y+h, x:x+w]

                # Transform purple borders to white
                cropped_hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
                purple_mask = cv2.inRange(cropped_hsv, lower_purple, upper_purple)
                cropped_image[purple_mask > 0] = [255, 255, 255]  # Set purple regions to white

                base_name = os.path.splitext(os.path.basename(input_image_path))[0]
                output_path = os.path.join(output_dir, f'{base_name}_cut_{image_counter}.png')
                cv2.imwrite(output_path, cropped_image)

                image_counter += 1

    print(f"Imagens processadas e salvas em '{output_dir}'.")

def main():

    pdf_file = "pdf/prova2024_dia2.pdf"
    output_images_dir = "output_images"
    cut_images_dir = "cut-imgs"
    page_images = extract_pages_as_images(pdf_file, output_dir=output_images_dir, scale_factor=3)
    process_and_cut_images(page_images, output_dir=cut_images_dir)
    shutil.rmtree(output_images_dir)

if __name__ == "__main__":
    main()
