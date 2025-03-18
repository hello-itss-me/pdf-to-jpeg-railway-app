from flask import Flask, request, jsonify, send_from_directory
import base64
from pdf2image import convert_from_bytes
from PIL import Image
import json
import io
import os
import uuid  # Для генерации уникальных имен файлов

app = Flask(__name__)

UPLOAD_FOLDER = 'images'  # Папка для сохранения JPEG изображений (относительно корня приложения)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Убедимся, что папка существует, иначе создадим ее
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['POST'])
def convert_pdf_to_jpeg():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({"error": "JSON должен содержать ключ 'data' с base64 строкой PDF"}), 400

        base64_string = data['data']
        pdf_bytes = base64.b64decode(base64_string)
        images = convert_from_bytes(pdf_bytes)

        image_urls = [] # Список для хранения URL-адресов изображений для каждой страницы
        for i, image in enumerate(images):
            # Генерируем уникальное имя файла для каждой страницы
            filename = f"{uuid.uuid4().hex}_page_{i+1}.jpeg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Сохраняем изображение в файл
            image.save(filepath, format='JPEG')

            # Формируем URL-адрес для доступа к изображению
            image_url = request.url_root + 'images/' + filename # request.url_root - базовый URL приложения

            image_urls.append(image_url)

        return jsonify({"success": True, "image_urls": image_urls}), 200 # Возвращаем список URL-адресов в JSON
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return jsonify({"error": f"Произошла ошибка: {e}"}), 500

# Маршрут для отдачи сохраненных изображений по URL-адресу
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
