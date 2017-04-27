import http.server
import socketserver
import os

PORT = 8080

web_dir = os.path.join(os.path.dirname(__file__), 'data')
os.chdir(web_dir)

Handler = http.server.SimpleHTTPRequestHandler
# httpd = socketserver.TCPServer(("104.198.0.87", PORT), Handler)
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()