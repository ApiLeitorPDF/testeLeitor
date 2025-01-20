import os
import fitz  # PyMuPDF
import cv2
import numpy as np
from paddleocr import PaddleOCR

# Use a more distinct purple color for the border
BORDER_COLOR = (255, 0, 255)  # Purple in BGR format for OpenCV
BORDER_THICKNESS = 3  # Adjust thickness; note that PyMuPDF uses points, not pixels
MIN_IMAGE_AREA = 50000  # Minimum area for border application
MAX_IMAGE_AREA = 5000000  # Maximum area for border application
PAGES_FOLDER = "uploads"
IMAGES_FOLDER = "questoesimg"
os.makedirs(PAGES_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)

ocr = PaddleOCR(use_angle_cls=True, lang='pt')

def add_border_to_images_in_pdf(input_pdf_path, output_pdf_path):
    """Adds purple borders around images in each page of the PDF."""
    pdf_document = fitz.open(input_pdf_path)
    output_document = fitz.open()

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        new_page = output_document.new_page(width=page.rect.width, height=page.rect.height)

        for img_index, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            base_image = pdf_document.extract_image(xref)
            if base_image is None:
                print(f"Error extracting image on page {page_number + 1}, index {img_index + 1}.")
                continue

            image_bytes = base_image["image"]
            width, height = base_image["width"], base_image["height"]
            image_area = width * height

            if not (MIN_IMAGE_AREA <= image_area <= MAX_IMAGE_AREA):
                continue

            try:
                image = np.frombuffer(image_bytes, np.uint8)
                cv_image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)

                # Draw border on the new page
                img_rect = page.get_image_bbox(img_info)
                border_rect = fitz.Rect(
                    img_rect.x0 - BORDER_THICKNESS,
                    img_rect.y0 - BORDER_THICKNESS,
                    img_rect.x1 + BORDER_THICKNESS,
                    img_rect.y1 + BORDER_THICKNESS
                )
                new_page.draw_rect(border_rect, color=(1, 0, 1), width=BORDER_THICKNESS)  # Purple in RGB

                # Insert the original image (without border) into the new page
                new_page.insert_image(img_rect, stream=image_bytes)

            except Exception as e:
                print(f"Error processing image on page {page_number + 1}, index {img_index + 1}: {e}")

        # Copy text from original page to new page
        new_page.show_pdf_page(new_page.rect, pdf_document, page_number)

    pdf_document.close()
    output_document.save(output_pdf_path)
    output_document.close()

def pdf_to_png(pdf_path):
    """Convert PDF pages to PNG images."""
    document = fitz.open(pdf_path)
    for page_number in range(len(document)):
        page = document[page_number]
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # Adjust DPI as needed
        png_path = os.path.join(PAGES_FOLDER, f"page_{page_number + 1}.png")
        pix.save(png_path)
    document.close()

def extract_bordered_images(folder_path):
    """Extract images within purple borders from PNG files."""
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.png'):
            image_path = os.path.join(folder_path, file_name)
            img = cv2.imread(image_path)
            height, width, _ = img.shape

            # Instead of thresholding, use color detection for the border
            lower_purple = np.array([120, 0, 120])  # Adjust these values based on your purple shade
            upper_purple = np.array([255, 100, 255])
            mask = cv2.inRange(img, lower_purple, upper_purple)

            # Find contours of purple regions
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for idx, cnt in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 100 and h > 100:  # Adjust these thresholds based on your needs
                    # Check if this contour could be an image with border
                    roi = img[y:y+h, x:x+w]
                    if np.any(np.all(roi[BORDER_THICKNESS, :, :] == BORDER_COLOR, axis=-1)):  # Check top border
                        # Extract the image inside the border
                        extraction = roi[BORDER_THICKNESS:-BORDER_THICKNESS, BORDER_THICKNESS:-BORDER_THICKNESS]
                        save_path = os.path.join(IMAGES_FOLDER, f"{file_name.split('.')[0]}_image_{idx}.png")
                        cv2.imwrite(save_path, extraction)

def perform_ocr_on_pdf(pdf_path):
    """Perform OCR on all pages of the PDF."""
    document = fitz.open(pdf_path)
    for page_number in range(len(document)):
        page = document[page_number]
        pix = page.get_pixmap()
        img = cv2.imdecode(np.frombuffer(pix.tobytes(), np.uint8), -1)
        ocr_results = ocr.ocr(img, cls=True)
        print(f"Texto extraído da página {page_number + 1}:")
        for line in ocr_results[0]:
            print(line[1][0])  # Print the text
    document.close()

if __name__ == '__main__':
    input_pdf_path = "/content/enem2024.pdf"
    output_pdf_path = "/content/enem2024bordas.pdf"

    try:
        # Add borders to images in PDF
        add_border_to_images_in_pdf(input_pdf_path, output_pdf_path)
        print(f"PDF processed successfully. File saved at: {output_pdf_path}")

        # Convert PDF with borders to PNG
        pdf_to_png(output_pdf_path)
        print("All pages converted to PNG.")

        # Extract images from within borders
        extract_bordered_images(PAGES_FOLDER)
        print("Images within borders extracted.")

        # Perform OCR on the modified PDF
        perform_ocr_on_pdf(output_pdf_path)

    except Exception as e:
        print(f"Error processing the PDF: {e}")
