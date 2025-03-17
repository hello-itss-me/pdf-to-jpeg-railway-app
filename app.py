from flask import Flask, request, jsonify
import base64
from pdf2image import convert_from_bytes
from PIL import Image
import json
import io
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def convert_pdf_to_jpeg():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({"error": "JSON должен содержать ключ 'data' с base64 строкой PDF"}), 400

        base64_string = data['data']
        pdf_bytes = base64.b64decode(base64_string)
        images = convert_from_bytes(pdf_bytes)

        jpeg_images_dict = {} # Словарь для хранения base64 строк, где ключ - "листN"
        for i, image in enumerate(images): # Используем enumerate для получения индекса страницы
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            jpeg_base64_string = base64.b64encode(img_byte_arr).decode('utf-8')
            page_number = i + 1 # Номера страниц начинаются с 1
            key_name = f"лист{page_number}" # Формируем ключ "лист1", "лист2", ...
            jpeg_images_dict[key_name] = jpeg_base64_string # Добавляем base64 строку в словарь

        return jsonify({"success": True, "pages": jpeg_images_dict}), 200 # Возвращаем словарь в JSON под ключом "pages"
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return jsonify({"error": f"Произошла ошибка: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
