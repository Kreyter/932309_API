import unittest
import json
from main import app
from io import BytesIO

class TestApp(unittest.TestCase):
    def test_get_time(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/Europe/Moscow'
        }
        response_body = self.get_response(environ)
        print("Test GET /Europe/Moscow: ", response_body)
        self.assertIn('Current time in Europe/Moscow', response_body)

    def test_convert_time(self):
        data = json.dumps({
            'date': '12.20.2021 22:21:05',
            'tz': 'EST',
            'target_tz': 'Europe/Moscow'
        }).encode('utf-8')
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/convert',
            'CONTENT_LENGTH': str(len(data)),
            'wsgi.input': BytesIO(data)
        }
        response_body = self.get_response(environ)
        print("Test POST /api/v1/convert: ", response_body)
        self.assertIn('converted_date', response_body)

    def test_datediff(self):
        data = json.dumps({
            'first_date': '12.06.2024 22:21:05',
            'first_tz': 'EST',
            'second_date': '12:30pm 2024-02-01',
            'second_tz': 'Europe/Moscow'
        }).encode('utf-8')
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/api/v1/datediff',
            'CONTENT_LENGTH': str(len(data)),
            'wsgi.input': BytesIO(data)
        }
        response_body = self.get_response(environ)
        print("Test POST /api/v1/datediff: ", response_body)
        self.assertIn('seconds_difference', response_body)

    def get_response(self, environ):
        def start_response(status, headers):
            pass

        result = app(environ, start_response)
        return b''.join(result).decode('utf-8')

if __name__ == '__main__':
    unittest.main()