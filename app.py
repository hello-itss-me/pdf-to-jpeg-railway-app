from flask import Flask, request, jsonify
import base64
from pdf2image import convert_from_bytes
from PIL import Image
import json
import io  # Для работы с байтовыми потоками изображений
import os  # Для доступа к переменным окружения

app = Flask(__name__)

@app.route('/', methods=['POST'])
def convert_pdf_to_jpeg():
    try:
        data = request.get_json() # Получаем JSON из тела запроса
        if not data or 'data' not in data:
            return jsonify({"error": "JSON должен содержать ключ 'data' с base64 строкой PDF"}), 400

        base64_string = data['data']
        pdf_bytes = base64.b64decode(base64_string)
        images = convert_from_bytes(pdf_bytes)

        if images:
            # Сохраняем первое изображение в байтовый поток в формате JPEG
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            jpeg_base64_string = base64.b64encode(img_byte_arr).decode('utf-8') # Кодируем в base64 для отправки в JSON

            return jsonify({"success": True, "jpeg_image": jpeg_base64_string}), 200 # Возвращаем base64 строку JPEG в JSON
        else:
            return jsonify({"error": "Не удалось конвертировать PDF в изображение"}), 400

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return jsonify({"error": f"Произошла ошибка: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) # Важно для Railway