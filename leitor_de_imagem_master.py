import fitz  # PyMuPDF
import os
import cv2
import pytesseract
import numpy as np

pytesseract = pytesseract.pytesseract
pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_images_from_pdf(pdf_path, output_dir):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Erro ao abrir o PDF: {e}")
        return

    for page_num in range(1, len(doc)-1):
        try:
            page = doc.load_page(page_num)
            images = page.get_images(full=True)
            if images:
                for img_index, img in enumerate(images):
                    base_xref, mask_xref = img[0], img[1]
                    base = fitz.Pixmap(doc, base_xref)
                    if base.colorspace != fitz.csRGB:
                        base = fitz.Pixmap(fitz.csRGB, base)
                    if mask_xref > 0:
                        mask = fitz.Pixmap(doc, mask_xref)
                        if mask.colorspace != fitz.csRGB:
                            mask = fitz.Pixmap(fitz.csRGB, mask)
                        pix = fitz.Pixmap(base, mask)
                        pix.save(f"{output_dir}/page_{page_num + 1}_image_{img_index + 1}.png")
                        pix = None
                        mask = None
                    else:
                        base.save(f"{output_dir}/page_{page_num + 1}_image_{img_index + 1}.png")
                    base = None
            else:
                print(f"Página {page_num + 1} não contém imagens.")
        except Exception as e:
            print(f"Erro ao processar a página {page_num + 1}: {e}")

    doc.close()

def pdf_to_img(pdf_path, pasta):
    try:
        mat = fitz.Matrix(2, 2)
        doc = fitz.open(pdf_path)
        page = doc.load_page(2)
        pix = page.get_pixmap(matrix=mat)
        pix.save(f"{pasta}/pagina10.png")
    except Exception as e:
        print(f"Erro ao abrir o PDF: {e}")
        return
    doc.close()

img = cv2.imread("pdf_para_img/pagina10.png")

def ler_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(thresh, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.medianBlur(img, 5)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    texto = pytesseract.image_to_string(img, lang="por")

    for letras in texto:
        if letras == "Q" and texto.startswith("QUESTÃO"):
            print("teste ")
        print(letras, end="")

    return texto



pdf_path = "pdf/2021super.pdf"
output_dir = "output_images"

pasta = "pdf_para_img"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

extract_images_from_pdf(pdf_path, output_dir)

if not os.path.exists(pasta):
    os.makedirs(pasta)

pdf_to_img(pdf_path, pasta)
ler_ocr(img)
