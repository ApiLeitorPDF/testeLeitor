
from flask import Flask, request, jsonify
import os
import PyPDF2
import pdfplumber
from PIL import Image
import fitz  # PyMuPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar diretório de uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def extract_text_from_pdf(file_path):
    """Extrai texto de um PDF."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


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
            import io
            image = Image.open(io.BytesIO(image_bytes))
            image_name = f"page_{page_number + 1}_image_{img_index + 1}.png"
            image.save(os.path.join(UPLOAD_FOLDER, image_name))
            images.append(image_name)
    return images


@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Endpoint para upload e processamento do PDF."""
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Extrair texto e imagens
    text = extract_text_from_pdf(file_path)
    images = extract_images_from_pdf(file_path)

    return jsonify({
        "text": text,
        "images": images
    })


if __name__ == '__main__':
    app.run(debug=True)
