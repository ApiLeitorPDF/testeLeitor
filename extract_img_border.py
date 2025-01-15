# -*- coding: utf-8 -*-

import fitz
import cv2
import numpy as np
import os

def extract_images_with_colored_borders(pdf_path, output_folder, upscale_factor=2):

    doc = fitz.open(pdf_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page_num in range(1, len(doc) - 1):

        pix = doc[page_num].get_pixmap()
        img_data = pix.tobytes("ppm")

        img_array = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            print(f"Falha ao processar a página {page_num + 1}.")
            continue

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        lower_red1 = np.array([0, 150, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 150, 50])
        upper_red2 = np.array([180, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

        lower_orange = np.array([15, 150, 50])
        upper_orange = np.array([25, 255, 255])
        mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)

        combined_mask = mask_blue | mask_red | mask_orange

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for i, contour in enumerate(contours):

            x, y, w, h = cv2.boundingRect(contour)

            if w > 50 and h > 50:
                cropped_img = img[y:y + h, x:x + w]

                new_width = int(cropped_img.shape[1] * upscale_factor)
                new_height = int(cropped_img.shape[0] * upscale_factor)
                resized_img = cv2.resize(cropped_img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

                output_path = os.path.join(output_folder, f"page_{page_num + 1}_image_{i + 1}.png")
                cv2.imwrite(output_path, resized_img)
                print(f"Imagem salva: {output_path}")

    doc.close()
    print("Processamento concluído!")

pdf_path = "pdf/2024ampliComBordas.pdf"
output_folder = "imagens_extraidas"
extract_images_with_colored_borders(pdf_path, output_folder, upscale_factor=2)
