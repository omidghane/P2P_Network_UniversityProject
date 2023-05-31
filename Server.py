import http.server
import json
import socket

import redis
from urllib.parse import urlparse, parse_qs

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/api/data':
            # Retrieve all data from Redis
            data = {key.decode(): value.decode() for key, value in redis_client.hgetall('data').items()}
            print(data, " dddddd")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        elif self.path.startswith('/api/data/address/'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            user = json.loads(post_data)
            address = redis_client.hget('data', user['id'])

            if address is not None:
                data = address.decode()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'User not found.')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found.')

    def do_POST(self):
        if self.path == '/api/data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            data = json.loads(post_data)
            # print(post_data)
            print(data, " post data")

            if 'id' in data and 'address' in data:
                # Store data in Redis
                redis_client.hset('data', data['id'], data['address'])
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Data stored successfully.')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid data format. Please provide data in JSON with "id" and "address".')

            return

        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not found.')


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Server running on http://localhost:8000')
    httpd.serve_forever()
