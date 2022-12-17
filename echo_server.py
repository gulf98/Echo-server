import socket
from http import HTTPStatus

HOST_AND_PORT = ("127.0.0.1", 20000)


def server_start(host_and_port=HOST_AND_PORT):
    with socket.socket() as server_socket:
        server_socket.bind(host_and_port)
        server_socket.listen()
        print(f"Server started on {host_and_port}")
        while True:
            (client_connection, client_address) = server_socket.accept()
            handle_client(client_connection, client_address)
            print(f"Sent data to {client_address}")


def handle_client(connection, address):
    data = ''
    with connection:
        while True:
            data_part = connection.recv(1024)
            if not data_part:
                break
            data += data_part.decode()
            if '\r\n\r\n' in data:
                break
        response = generate_response(data, address)
        connection.send(response)


def generate_response(data, address):
    lines = data.splitlines()
    method, path, version = lines[0].split()
    status = generate_status(path)
    headers = ""
    for line in lines[1:-1]:
        key, value = line.split(": ", 1)
        headers += f"\r\n{key}: {value}"
    body = f"Request Method: {method}" \
           f"\r\nRequest Source: {address}" \
           f"\r\nResponse Status: {status}" \
           f"{headers}"
    response = f"{version} {status}" \
               f"{headers}" \
               f"\r\n\r\n" \
               f"{body}"
    return response.encode()


def generate_status(path):
    if "status" not in path:
        return "200 OK"
    try:
        index = path.find("=")
        status = int(path[index + 1:])
    except ValueError:
        return "200 OK"
    if status not in [s.value for s in HTTPStatus]:
        return "200 OK"
    return f"{status} {HTTPStatus(status).name}"


if __name__ == "__main__":
    server_start()
