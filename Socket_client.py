import socket
import time

HOST = '127.0.0.1'

PORT = 9999       


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client_socket.connect((HOST, PORT))

def ReqTest(buffSz):
    client_socket.sendall('Req Test'.encode())
    
    send = 't' * (buffSz - 33) # 33 + size
    send = send.encode()
    print(send.__sizeof__())
    start = time.time_ns()
    client_socket.sendall(send)
    end = client_socket.recv(1024)
    endt = time.time_ns()
    if end == send:
        dur = endt - start
        dur *= 10e-9
        print(dur)
    else:
        print(end.decode())

def DownloadTest():
    client_socket.sendall('Download Test'.encode())

    import cv2

    path = "D:\PlayVideo\V1\Frames\F1.png"
    im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    send = cv2.imencode('.png', im)[1].tobytes()
    print(send.__sizeof__())
    start = time.time_ns()
    client_socket.sendall(send)
    end = client_socket.recv(2620728)
    endt = time.time_ns()
    if end == send:
        dur = endt - start
        dur *= 10e-9
        print(dur)
    else:
        print(end)

while True:
    state = input('r for Req test, d for Download test, e for close')
    if state == 'r':
        minR = 20
        maxR = 40
        delay = 1
        for sz in range(34 + minR, 34 + maxR):
            ReqTest(sz)
            time.sleep(delay)
    elif state == 'd':
        for i in range(5):
            DownloadTest()
    elif state == 'e':
        break

client_socket.close()