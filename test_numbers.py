import sqlite3
import unittest
import json

import main
from main import app, init_db


def clear_db():
    """Очищает таблицу numbers."""


with sqlite3.connect(main.DATABASE) as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM numbers")
    conn.commit()


class ProcessNumberTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()
        clear_db()

    def test_valid_number(self):
        response = self.app.post('/numbers', data=json.dumps({'number': 2}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['result'], 3)

    def test_number_already_exists(self):
        self.app.post('/numbers', data=json.dumps({'number': 1}), content_type='application/json')
        response = self.app.post('/numbers', data=json.dumps({'number': 1}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Number 1 already exists.', response.json['error'])

    def test_number_minus_one_exists(self):
        self.app.post('/numbers', data=json.dumps({'number': 2}), content_type='application/json')
        response = self.app.post('/numbers', data=json.dumps({'number': 1}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Number 1 already exists.', response.json['error'])

    def test_invalid_input_missing_number(self):
        response = self.app.post('/numbers', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid input: Missing "number"', response.json['error'])

    def test_invalid_input_non_integer(self):
        response = self.app.post('/numbers', data=json.dumps({'number': 'a'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid input: Number must be an integer.', response.json['error'])

    def test_number_out_of_range(self):
        response = self.app.post('/numbers', data=json.dumps({'number': 0}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Number out of range', response.json['error'])


if __name__ == '__main__':
    unittest.main()
