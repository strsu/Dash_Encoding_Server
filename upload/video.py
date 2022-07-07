import socket

def message(videoName):
    Host = '127.0.0.1' # 연결할 서버의 외부 IP 주소
    Port = 4000        # 연결할 서버의 포트번호

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((Host, Port))

    client_socket.sendall(('h'+videoName).encode())
    client_socket.close()