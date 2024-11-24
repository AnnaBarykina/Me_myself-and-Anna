import sqlite3
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE = 'numbers.db'


def init_db():
    """Создает таблицу, если её нет."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS numbers (
                number INTEGER PRIMARY KEY CHECK (number >= 0)
            )
        ''')
        conn.commit()


def get_last_number():
    """Возвращает последнее обработанное число."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(number) FROM numbers")
        last_number = cursor.fetchone()[0]
    return last_number if last_number is not None else -1


def add_number(number):
    """Добавляет число в базу данных. Возвращает True, если успешно."""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO numbers (number) VALUES (?)", (number,))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        logger.error(f"IntegrityError: Number {number} already exists.")
        return False
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False


@app.route('/numbers', methods=['POST'])
def process_number():
    """Обрабатывает POST-запрос для числа."""
    try:
        # Получение и проверка входных данных
        data = request.get_json()
        if not data or 'number' not in data:
            return jsonify({'error': 'Invalid input: Missing "number"'}), 400

        number = int(data['number'])
        if not 0 <= number <= 10000:  # Пример ограничения диапазона
            return jsonify({'error': 'Number out of range'}), 400

        # Получение последнего обработанного числа
        last_number = get_last_number()
        if number <= last_number:
            error_message = (f"Error: Number already exists or is less than or equal to "
                             f"the last processed number (N={number}, last={last_number})")
            logger.error(error_message)
            return jsonify({'error': error_message}), 400

        # Добавление числа в базу данных
        if add_number(number):
            return jsonify({'result': number + 1}), 200
        else:
            return jsonify({'error': 'Database error'}), 500

    except ValueError:
        logger.error("Invalid input: Number must be an integer.")
        return jsonify({'error': 'Invalid input: Number must be an integer.'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
