import json
from datetime import datetime
from pytz import timezone, all_timezones
from wsgiref.simple_server import make_server

def app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')
    if method == 'GET' and path.startswith('/'):
        tz_name = path[1:] if len(path) > 1 else 'GMT'
        if tz_name not in all_timezones:
            start_response('400 Bad Request', [('Content-Type', 'text/html')])
            return [b'Invalid timezone']
        now = datetime.now(timezone(tz_name))
        response_body = f"<html><body>Current time in {tz_name}: {now.strftime('%Y-%m-%d %H:%M:%S')}</body></html>"
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]

    elif method == 'POST' and path == '/api/v1/convert':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            date_str = data['date']
            from_tz = data['tz']
            to_tz = data['target_tz']
            if from_tz not in all_timezones or to_tz not in all_timezones:
                raise ValueError('Invalid timezone')
            date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
            from_zone = timezone(from_tz)
            to_zone = timezone(to_tz)
            date = from_zone.localize(date).astimezone(to_zone)
            response_body = json.dumps({'converted_date': date.strftime('%Y-%m-%d %H:%M:%S')})
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [response_body.encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]

    elif method == 'POST' and path == '/api/v1/datediff':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            first_date_str = data['first_date']
            first_tz = data['first_tz']
            second_date_str = data['second_date']
            second_tz = data['second_tz']
            if first_tz not in all_timezones or second_tz not in all_timezones:
                raise ValueError('Invalid timezone')
            first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
            second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
            first_zone = timezone(first_tz)
            second_zone = timezone(second_tz)
            first_date = first_zone.localize(first_date)
            second_date = second_zone.localize(second_date)
            diff = (second_date - first_date).total_seconds()
            response_body = json.dumps({'seconds_difference': diff})
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [response_body.encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]

    start_response('404 Not Found', [('Content-Type', 'text/html')])
    return [b'Not Found']

if __name__ == '__main__':
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")
    httpd.serve_forever()