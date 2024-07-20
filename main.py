import network
import usocket
import ure

from html_stuff import generate_settings_page, search_xml
from unquote import unquote
from ssid import ssid

delete_regex = ure.compile(".*delete-([^&]*)&.*")

wlan = network.WLAN(network.STA_IF)

def load_redirects():
    redirects = {}
    try:
        with open('redirects.txt') as f:
            for line in f:
                path, url = line.strip().split(' ')
                redirects[path] = url
    except OSError:
        print('Error: Could not open redirects.txt')
    return redirects

def save_redirects(redirects):
    with open('redirects.txt', 'w') as f:
        for path, url in redirects.items():
            f.write(f'{path} {url}\n')

redirects = load_redirects()

def start():
    global redirects
    wlan.active(True)
    wlan.connect(ssid["name"], ssid["password"])

    while not wlan.isconnected():
        pass

    pico_ip = wlan.ifconfig()[0]
    print('Pico W IP address:', pico_ip)

    s = usocket.socket()
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        request_data = b''
        content_length = 0  
        is_post = False

        # Read headers and determine content length and request method
        while True:
            data = conn.recv(8192)
            if not data:
                break
            request_data += data

            # Check for end of headers
            if b'\r\n\r\n' in request_data:
                header_end = request_data.find(b'\r\n\r\n')
                headers = request_data[:header_end].decode()
                # Check if it's a POST request
                is_post = headers.startswith('POST')
                
                for line in headers.split('\r\n'):
                    if line.startswith('Content-Length:'):
                        content_length = int(line.split(': ')[1])
                break

        # Read the request body if it's a POST request
        if is_post and content_length > 0:
            while len(request_data) < header_end + 4 + content_length:  # 4 for \r\n\r\n
                data = conn.recv(8192)
                if not data:
                    break
                request_data += data
    

        request_text = request_data.decode()
        request_lines = request_text.split('\r\n')
        try:
            method, full_path, _ = request_lines[0].split(' ')
        except Exception as e:
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'

        path = full_path.split('?')[0]

        print(request_data) # Just for logging purposes while connected to a computer

        if path == '/settings':
            if method == 'POST':
                body = request_text.split("\n")[-1]
                unquoted = unquote(body).decode()
                if unquoted.startswith("action=delete"):
                    to_delete = "/" + delete_regex.match(unquoted).groups()[0].split("=")[1]
                    print(to_delete)
                    del redirects[to_delete]
                else:
                    assignments = unquoted.split("&")
                    for i in range(0, len(assignments)/2):
                        path = assignments[2*i]
                        url = assignments[2*i+1]
                        print(path, url)
                        path = path.split('=')[1]
                        if path[0] != "/":
                            path = "/" + path
                        url = url.split('=')[1]
                        redirects[path] = url
                        print(f"Path: {path}, URL: {url}") 
                save_redirects(redirects)

            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + generate_settings_page(redirects)
        elif path == '/redirect_search.xml': # This can work with Safari, in theory, for custom domain search
            # Format the XML with the actual IP address, just in case resolution is spotty
            response = 'HTTP/1.1 200 OK\r\nContent-Type: application/xml\r\n\r\n' + search_xml
        elif path in redirects:
            # Redirect if found
            redirect_url = redirects[path]
            response = f'HTTP/1.1 302 Found\r\nLocation: {redirect_url}\r\n\r\n'
        else:
            # 404 if not found
            response = 'HTTP/1.1 404 Not Found\r\n\r\n'

        conn.send(response)
        conn.close()

start()