import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_dir):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Erro ao abrir o PDF: {e}")
        return

    for page_num in range(len(doc)):
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

pdf_path = "prova2024completa.pdf"
output_dir = "output_images"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

extract_images_from_pdf(pdf_path, output_dir)
