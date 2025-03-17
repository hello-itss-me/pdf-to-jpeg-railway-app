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
        images = convert_from_bytes(pdf_bytes) # Теперь images - это список PIL Image objects

        jpeg_base64_strings = [] # Список для хранения base64 строк JPEG для каждой страницы
        for image in images: # Итерируем по списку изображений (страниц)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            jpeg_base64_string = base64.b64encode(img_byte_arr).decode('utf-8')
            jpeg_base64_strings.append(jpeg_base64_string) # Добавляем base64 строку в список

        return jsonify({"success": True, "jpeg_images": jpeg_base64_strings}), 200 # Возвращаем список base64 строк в JSON
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return jsonify({"error": f"Произошла ошибка: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
