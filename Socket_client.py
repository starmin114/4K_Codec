import socket
import time

import csv
import os


HOST = '127.0.0.1'
PORT = 8080


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def ReqTest(buffSz):   
    send = 't' * (buffSz)
    send = send.encode()
    print(send.__sizeof__())
    start = time.time()
    client_socket.sendall(send)
    dur = time.time()
    dur -= start
    dur *= 10e-3
    print(dur)
    return dur

def DownloadTest():
    import cv2

    path = "D:\PlayVideo\V1\Frames\F1.png"
    im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    send = cv2.imencode('.png', im)[1].tobytes()
    print(send.__sizeof__())
    start = time.time_ns()
    client_socket.sendall(send)
    dur = time.time_ns()
    dur -= start
    dur *= 10e-9
    print(dur)
    return dur

def PingTest(num, writer):
    import asyncio
    t = 0
    delay = 1/60
    allt = 0
    async def wait_for_data(send):
        loop = asyncio.get_running_loop()

        # Simulate the reception of data from the network
        for j in range(12):
            
            future = []
            for index in range(num):
                print(f"[{index}]Sending..")
                t = time.time()
                future.append(asyncio.ensure_future(loop.sock_sendall(client_socket, send)))
                data = await loop.sock_recv(client_socket, 9620727)
                print(f"[{index}]Received:", data.__sizeof__())
                if index == 0: allt = t
                a = delay - time.time() + t
                # print(a)
                await asyncio.sleep(a)
                # Got data, we are done: close the socket
            
            b = str(time.time() - allt)
            writer.writerow([data.__sizeof__(), b])
            print('total t :: ' + b)

    
    asyncio.run(wait_for_data(('t' * (16)).encode()))
    
    return 1


delay = 2
while True:
    state = input('r for Req test, d for Download test, p for Ping test, e for close')
    if state == 'r':
        num = int(input('how many times?'))
        dur = 0
        client_socket.sendall(f'Req Test'.encode())
        client_socket.sendall(str(num).encode())
        time.sleep(delay)
        for i in range(num):
            dur += ReqTest(16)
            print(i+1)
            time.sleep(delay)
        print(dur)
                
    elif state == 'd':
        num = int(input('how many times?'))
        dur = 0
        client_socket.sendall(f'Download Test'.encode())
        client_socket.sendall(str(num).encode())
        time.sleep(delay)
        for i in range(num):
            dur += DownloadTest()
            print(i+1)
            time.sleep(delay)
        print(dur)
    
    elif state == 'p':
        csvdirpath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csvdirpath = os.path.join(csvdirpath, "Result")
        with open(os.path.join(csvdirpath, "PingTest.csv"), 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['Size', 'Latency'])
            
            num = int(input('how many times?'))
            dur = 0
            client_socket.sendall(f'Ping Test'.encode())
            client_socket.sendall(str(num).encode())
            time.sleep(delay)
            client_socket.setblocking(False)
            PingTest(num, writer)
            client_socket.setblocking(True)
        
    elif state == 'e':
        break

client_socket.close()
