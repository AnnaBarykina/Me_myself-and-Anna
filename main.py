import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import IntegrityError, DatabaseError
from flask import Flask, request, jsonify
import logging

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'mydatabase'),
    'user': os.getenv('POSTGRES_USER', 'myuser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'mypassword'),
    'host': 'localhost',
    'port': 5432
}


def get_last_number():
    """Возвращает последнее обработанное число."""
    query = "SELECT MAX(number) FROM numbers"
    try:
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                if row is None or row[0] is None:
                    return -1
                return row[0]
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return -1


def add_number(number):
    """Добавляет число в базу данных. Возвращает True, если успешно."""
    insert_query = "INSERT INTO numbers (number) VALUES (%s)"
    try:
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_query, (number,))
            conn.commit()
        return True
    except IntegrityError:
        logger.error(f"IntegrityError: Number {number} already exists.")
        return False
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return False


@app.route('/numbers', methods=['POST'])
def process_number():
    """Обрабатывает POST-запрос для числа."""
    try:
        data = request.get_json()

        # Валидация входных данных
        if not data or 'number' not in data:
            return jsonify({'error': 'Invalid input: Missing "number"'}), 400

        number = int(data['number'])
        if number <= 0:
            return jsonify({'error': 'Number out of range'}), 400

        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor() as cursor:
                # Проверяем, есть ли число в БД
                cursor.execute("SELECT 1 FROM numbers WHERE number = %s", (number,))
                if cursor.fetchone():
                    logger.error(f"Error: Number {number} already exists.")
                    return jsonify({'error': f"Number {number} already exists."}), 400

                # Проверяем, есть ли number - 1 в БД
                cursor.execute("SELECT 1 FROM numbers WHERE number = %s", (number - 1,))
                if cursor.fetchone():
                    logger.error(f"Error: Number {number - 1} already exists.")
                    return jsonify({'error': f"Number {number - 1} already exists."}), 400

                # Добавляем число в БД
                cursor.execute("INSERT INTO numbers (number) VALUES (%s)", (number,))
            conn.commit()

        return jsonify({'result': number + 1}), 200

    except ValueError:
        logger.error("Invalid input: Number must be an integer.")
        return jsonify({'error': 'Invalid input: Number must be an integer.'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)