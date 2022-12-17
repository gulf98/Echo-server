import socket
from http import HTTPStatus

HOST_AND_PORT = ("127.0.0.1", 20000)


def server_start(host_and_port=HOST_AND_PORT):
    with socket.socket() as serverSocket:
        serverSocket.bind(host_and_port)
        serverSocket.listen()
        print(f"Server started on {host_and_port}")
        while True:
            (clientConnection, clientAddress) = serverSocket.accept()
            handle_client(clientConnection)
            print(f"Sent data to {clientAddress}")


def handle_client(connection):
    client_data = ''
    with connection:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            client_data += data.decode()
            if '\r\n\r\n' in client_data:
                break
        response = generate_response(client_data)
        connection.send(response)


def generate_response(client_data, host_and_port=HOST_AND_PORT):
    lines = client_data.splitlines()
    method, path, http_version = lines[0].split()
    status = get_status(path)
    headers = ""
    for line in lines[1:-1]:
        key, value = line.split(": ", 1)
        headers += f"\r\n{key}: {value}"
    response_body = f"Request Method: {method}" \
                    f"\r\nRequest Source: {host_and_port}" \
                    f"\r\nResponse Status: {status}" \
                    f"{headers}"
    response = f"{http_version} {status}" \
               f"{headers}" \
               f"\r\n\r\n" \
               f"{response_body}"
    return response.encode()


def get_status(path):
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
