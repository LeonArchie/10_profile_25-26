# ИМПОРТ НЕОБХОДИМЫХ КОМПОНЕНТОВ ИЗ Flask
# flask - библиотека для создания веб-приложений; Flask - класс внутри библиотеки
# jsonify - для отправки данных пользователю
from flask import Flask, jsonify

# Вычисляем максимальные и минимальные значения для 64-битных чисел
MAX_UNSIGNED_64BIT = (1 << 64) - 1
MIN_SIGNED_64BIT = -(1 << 63)
MAX_SIGNED_64BIT = (1 << 63) - 1

# Flask использует __name__, чтобы определить: файл запущен напрямую или импортирован как модуль
app = Flask(__name__)
# Проверка жив или нет
@app.route('/livez', methods=['GET'])
def livez():
    return jsonify({"status": "alive"}), 200
# Проверка здоровья (готов к работе с пользователем или нет)
@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "healthy"}), 200
# Проверка готовности принимать трафик
@app.route('/readyz', methods=['GET'])
def readyz():
    return jsonify({"status": "ready"}), 200

# Возвращение инф о доступных операциях конвертации
@app.route('/convert', methods=['GET'])
def convert_info():
    return jsonify({
        "service": "Number System Converter",
        "description": "Converts numbers between decimal, binary and hexadecimal systems",
        "available_endpoints": {
            "get_systems": "/convert/systems",
            "decimal_to_binary": "/convert/dec-to-bin/<number>",
            "decimal_to_hexadecimal": "/convert/dec-to-hex/<number>", 
            "binary_to_decimal": "/convert/bin-to-dec/<number>",
            "hexadecimal_to_decimal": "/convert/hex-to-dec/<number>"
        },
        "limits": {
            "max_number": str(MAX_UNSIGNED_64BIT),
            "min_number": str(MIN_SIGNED_64BIT),
            "max_binary_length": 64,
            "max_hex_length": 16
        }
    }), 200


@app.route('/convert/systems', methods=['GET'])
#Возвращает список поддерживаемых систем счисления
def get_systems():
    return jsonify({"systems": ["binary", "decimal", "hexadecimal"]}), 200

# Эндпоинт для перевода из десятичной в двоичную
@app.route('/convert/dec-to-bin/<int:number>', methods=['GET']) 
def dec_to_bin(number):
    try:
        # Проверка нахождения в диапазоне для 64-битного представления
        if number > MAX_UNSIGNED_64BIT or number < MIN_SIGNED_64BIT:
            return jsonify({
                "error": f"Number out of range. Allowed range: {MIN_SIGNED_64BIT} to {MAX_UNSIGNED_64BIT}"
            }), 400

        # Для отрицательных чисел
        if number < 0:
            # Преобразуем отрицательное число в его 64-битное беззнаковое представление
            # Т.е прибавляем 2^64 к отрицательному числу
            unsigned_representation = (1 << 64) + number
            binary_string = bin(unsigned_representation)[2:]  # Убираем '0b' в начале
        else:
            # Просто положительные числа
            binary_string = bin(number)[2:]
        return jsonify({
            "decimal": number,
            "binary": binary_string
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 400

# Эндпоинт для перевода из десятичной в шестнадцатеричную 
@app.route('/convert/dec-to-hex/<int:number>', methods=['GET'])
def dec_to_hex(number):
    try:
        #Тоже проверка диапазона
        if number > MAX_UNSIGNED_64BIT or number < MIN_SIGNED_64BIT:
            return jsonify({
                "error": f"Number out of range. Allowed range: {MIN_SIGNED_64BIT} to {MAX_UNSIGNED_64BIT}"
            }), 400
        # Отрицательные числа
        if number < 0:
            unsigned_representation = (1 << 64) + number
            hex_string = hex(unsigned_representation)[2:].upper()  # Убираем '0x', upper() для заглавных букв
        else:
            hex_string = hex(number)[2:].upper()  # Убираем '0x', upper() для заглавных букв

        return jsonify({
            "decimal": number,
            "hexadecimal": hex_string
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 400

# Эндпоинт для перевода из двоичной в десятичную
@app.route('/convert/bin-to-dec/<string:binary_string>', methods=['GET'])
def bin_to_dec(binary_string):
    try:
        # Проверка, что строка содержит только 0 и 1
        if not all(bit in '01' for bit in binary_string):
            return jsonify({"error": "Invalid binary number. Only characters '0' and '1' are allowed"}), 400
        
        # Проверка длины (макс. 64 бита)
        if len(binary_string) > 64:
            return jsonify({"error": "Binary number too long. Maximum 64 bits allowed"}), 400
        
        # Конвертируем двоичную строку в целое число
        unsigned_value = int(binary_string, 2)
        
        # Является ли число отрицательным?
        # Если число имеет 64 бита и старший бит равен 1, то это отрицательное число
        if len(binary_string) == 64 and binary_string[0] == '1':
            # Преобразуем 
            decimal_value = unsigned_value - (1 << 64)
        else:
            decimal_value = unsigned_value
        
        return jsonify({
            "decimal": decimal_value,
            "binary": binary_string
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 400

# Эндпоинт для перевода из шестнадцатеричной в десятичную
@app.route('/convert/hex-to-dec/<string:hex_string>', methods=['GET'])
def hex_to_dec(hex_string):
    try:
        # Валидация: проверка, что строка содержит только шестнадцатеричные символы
        if not all(c in '0123456789ABCDEFabcdef' for c in hex_string):
            return jsonify({"error": "Invalid hexadecimal number. Only characters 0-9, A-F, a-f are allowed"}), 400
        
        # Проверяка длины (макс. 16 символов для 64 бит)
        if len(hex_string) > 16:
            return jsonify({"error": "Hexadecimal number too long. Maximum 16 characters allowed"}), 400

        # Конвертиртация шестнадцатеричной строки в целое число
        unsigned_value = int(hex_string, 16)
        
        # Является ли число отрицательным?
        # Если значение >= 2^63, то в 64-битном представлении это отрицательное число
        if unsigned_value >= (1 << 63):
            # Преобразуем
            decimal_value = unsigned_value - (1 << 64)
        else:
            decimal_value = unsigned_value
        
        return jsonify({
            "decimal": decimal_value,
            "hexadecimal": hex_string.upper()  # Приводим к верхнему регистру
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 400


































        