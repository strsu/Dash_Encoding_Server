import socket
import threading
from queue import Queue
import time
import os
from typing import final
from collections import deque

from video_encoding import h264_encoding, dash_encoding

class Receiver(threading.Thread):
    def __init__(self, msgQ, client_socket, addr):
        super().__init__()
        self.msgQ = msgQ
        self.client_socket = client_socket
        self.addr = addr
        self.size = 102400
        self.user_name = os.path.expanduser('~')

    def run(self):
        try:
            data = self.client_socket.recv(self.size)
            if data:
                msg = data.decode()
                self.msgQ.put([self.client_socket, msg])
        finally: # 예외처리 필수
            # 프로그램 종료시, 종료된 사용자를 지우기 위한 작업
            # 이 작업이 없다면 무한루프에 빠져 이후 통신이 불가능해진다.
            client_socket_queue.put((self.client_socket, self.addr))
            return True

class Manager(threading.Thread):
    def __init__(self, clientQ, msgQ):
        super().__init__()
        self.clientQ = clientQ
        self.msgQ = msgQ

        self.client = {}
        self.h264_worker = None
        self.p360_worker = None
        self.p720_worker = None
        self.h264Q = deque([])
        self.p360Q = deque([])
        self.p720Q = deque([])

    def run(self):
        while True:
            if self.clientQ.qsize() > 0:
                client_socket, addr = self.clientQ.get()
                if client_socket in self.client:
                    del self.client[client_socket]
                else:
                    self.client[client_socket] = addr
            
            if self.msgQ.qsize() > 0:
                client, data = self.msgQ.get()
                if data[0] == 'h':
                    self.h264Q.append(data[1:])
                else:
                    self.p360Q.append(data[1:])
                    self.p720Q.append(data[1:])
            
            if self.h264Q and self.h264_worker == None:
                data = self.h264Q.popleft()
                self.h264_worker = threading.Thread(target=h264_encoding, args=(data, ))
                self.h264_worker.start()
            else:
                if self.h264_worker != None:
                    if not self.h264_worker.is_alive():
                        self.h264_worker = None
            
            if self.p360Q and self.p360_worker == None:
                data = self.p360Q.popleft()
                print('p360', data)
                self.p360_worker = threading.Thread(target=dash_encoding, args=(data, 360, 240))
                self.p360_worker.start()
            else:
                if self.p360_worker != None:
                    if not self.p360_worker.is_alive():
                        self.p360_worker = None
            
            if self.p720Q and self.p720_worker == None:
                data = self.p720Q.popleft()
                print('p720', data)
                self.p720_worker = threading.Thread(target=dash_encoding, args=(data, 720, 480))
                self.p720_worker.start()
            else:
                if self.p720_worker != None:
                    if not self.p720_worker.is_alive():
                        self.p720_worker = None


if __name__ == "__main__":

    Host = '0.0.0.0' # 서버는 0.0.0.0으로 바인딩
    Port = 4000      # 사용할 포트

    # 소켓 객체를 생성
    # 주소 체계 IPv4, TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 포트 사용중이라 연결할 수 없다는
    # WinError 10048 에러 해결을 위해 필요
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind 함수는 소켓을 특정 네트워크 인터페이스와 포트 번호에 연결하는데 사용
    server_socket.bind((Host, Port))

    # 서버가 클라이언트의 접속을 허용하도록
    server_socket.listen()

    client_socket_queue = Queue()
    client_data_queue = Queue()

    #sender = threading.Thread(target=Sender, args=(client_socket_queue, client_data_queue))
    manager = Manager(client_socket_queue, client_data_queue)
    manager.start()

    receiver = []

    while True:

        # accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓을 리턴
        client_socket, addr = server_socket.accept()
        client_socket_queue.put((client_socket, addr))

        receiver_ = Receiver(client_data_queue, client_socket, addr)
        receiver_.start()
        receiver.append(receiver_)

        #print('new client access', addr, client_socket_queue)


    client_socket.close()
    server_socket.close()