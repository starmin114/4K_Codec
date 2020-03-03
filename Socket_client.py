import socket
import time

import csv
import os

HOST = '127.0.0.1'
# HOST = '1.233.226.101'

PORT = 8080


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client_socket.connect((HOST, PORT))

print(client_socket.getblocking())

def ReqTest(buffSz, wr):
    client_socket.sendall('Req Test'.encode())
    
    send = 't' * (buffSz - 33) # 33 + size
    send = send.encode()
    print(send.__sizeof__())
    start = time.time()
    client_socket.sendall(send)
    dur = time.time()
    dur -= start
    end = client_socket.recv(2620727)
    if end == send:
        dur *= 10e-3
        print(dur)
        return dur
    else:
        print(end.decode())

def DownloadTest(wr):
    client_socket.sendall('Download Test'.encode())

    import cv2

    path = "D:\PlayVideo\V1\Frames\F1.png"
    im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    send = cv2.imencode('.png', im)[1].tobytes()
    print(send.__sizeof__())
    start = time.time_ns()
    client_socket.sendall(send)
    midt = time.time_ns()
    end = client_socket.recv(1)
    dur = time.time_ns()
    dur -= start
    if end.decode() == '1':
        dur *= 10e-9
        # wr.writerow([dur])
        print(dur)
        print((midt-start)*10e-9)
        return dur
    else:
        print(end)

csvdirpath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
csvdirpath = os.path.join(csvdirpath, "Result")
delay = 3
while True:
    state = input('r for Req test, d for Download test, e for close')
    if state == 'r':
        minR = 20
        maxR = 40
       

        with open(os.path.join(csvdirpath, "ReqTest_2.csv"), 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['Latency'])
            num = int(input('how many times?'))
            for i in range(num):
                dur = 0
                for j in range(5):
                    dur += ReqTest(2620725, writer)
                    print(j+1)
                    time.sleep(delay)
                
                print(dur)
                writer.writerow([dur])
                
                
                
    elif state == 'd':
        with open(os.path.join(csvdirpath, "DownLinkTest_3.csv"), 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['Latency'])
            num = int(input('how many times?'))
            for i in range(num):
                dur = 0
                for j in range(20):
                    dur += DownloadTest(writer)
                    print(j+1)
                    time.sleep(delay)
                
                
                print(dur)
                writer.writerow([dur])
                
        
    elif state == 'e':
        break

client_socket.close()