import socket
import time
import asyncio

HOST = '127.0.0.1'

PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


server_socket.bind((HOST, PORT))

server_socket.listen()

client_socket, addr = server_socket.accept()



print('Connected by', addr)

state = 0
num = 0

cnt = 0

async def handle(send, index):
    print(f"[{index}]Sending..{send.__sizeof__()}")
    client_socket.sendall(send)

async def wait_for_data(num):
    loop = asyncio.get_running_loop()

    # # Register the open socket to wait for data.
    # # reader, writer = await asyncio.open_connection(sock=client_socket)

    # # Wait for data
    # data = await data.recv(100)

    # # Got data, we are done: close the socket
    # print(f"[{index}]Received:", data.decode())

    # Simulate the reception of data from the network

    # await writer.drain()
    # cnt += 1
    
    # writer.close()
    # await asyncio.sleep(10)
    for j in range(10):
        send = ('t' * (5000 * pow(2,j+2))).encode()
        future = []

        for i in range(num):
            data = await loop.sock_recv(client_socket, 16)
            print(f"[{i}]Received:", data.decode().__sizeof__())
            future.append(asyncio.ensure_future(loop.sock_sendall(client_socket, send)))
            
        i = 0
        for f in asyncio.as_completed(future):
            i += 1
            await f
            print(f"[{i}]Sending..{send.__sizeof__()}")
    
    # loop.close()
    

def aDownloadTest(num):
    import asyncio
    t = 0
    delay = 1/60
    allt = 0
    async def wait_for_data(send):
        loop = asyncio.get_running_loop()

        # Simulate the reception of data from the network
        for j in range(12):
            send = ('t' * (5000 * pow(2,j))).encode()
            future = []

            for i in range(num):
                # data = await loop.sock_recv(client_socket, 16)
                # print(f"[{i}]Received:", data.decode().__sizeof__())
                t = time.time()
                future.append(asyncio.ensure_future(loop.sock_sendall(client_socket, send)))
                
                # await loop.sock_sendall(client_socket, send)
                # print(f"[{i}]Sending..{send.__sizeof__()}")
                a = delay - time.time() + t
                print(a)
                # await asyncio.sleep(a)
                time.sleep(a)

            i = 0
            for f in asyncio.as_completed(future):
                i += 1
                await f
                print(f"[{i}]Sending..{send.__sizeof__()}")
            time.sleep(2)

    
    asyncio.run(wait_for_data(('t' * (16)).encode()))
    
    return 1

while True:
    data = client_socket.recv(2620727)
    if not data:
        break
    

    if(state == 'R'):
        #client_socket.send('Send Req data.'.encode())
        print('Message:', data.__sizeof__())
        num -=1
        if num==0:
            state = 0
    elif(state == 'D'):
        #client_socket.send('Send Req data.'.encode())
        print('Message:', data.__sizeof__())
        num -=1
        if num==0:
            state = 0

    elif(state == 0):
        if(data.decode() == 'Req Test'):
            print('<<Req Latency Test Start!>>')
            state = 'R'
        elif(data.decode() == 'Download Test'):
            print('<<Download Latency Test Start!>>')
            state = 'D'
        elif(data.decode() == 'Ping Test'):
            print('<<Ping Latency Test Start!>>')
            state = 'P'
        elif(data.decode() == 'aDownload Test'):
            print('<<aDownload Latency Test Start!>>')
            state = 'aD'

        data = client_socket.recv(2620727)
        num = int(data.decode())
        print('Received from Client:', addr, 'Message:', data.decode())

    
    if(state == 'P'):
        # import cv2
        # path = "C:\\Users\\jaine\\Desktop\\F1.png"
        # path = 'D:\PlayVideo\V1\Frames\F1.png'
        # im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        # send = cv2.imencode('.png', im)[1].tobytes()

        client_socket.setblocking(False)
        
        cnt = 0

        # for i in range(11):
        asyncio.run(wait_for_data(num))
            
        print('end')
        state = 0
        client_socket.setblocking(True)

    elif(state == 'aD'):
        client_socket.setblocking(False)
        asyncio.run(aDownloadTest(num))
            
        print('end')
        state = 0
        client_socket.setblocking(True)
    
client_socket.close()
server_socket.close()
