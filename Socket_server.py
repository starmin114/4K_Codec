import socket
import time

HOST = '127.0.0.1'

PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


server_socket.bind((HOST, PORT))

server_socket.listen()

client_socket, addr = server_socket.accept()

print('Connected by', addr)

state = 0
while True:
    data = client_socket.recv(2620727)
    st = time.time_ns()
    if not data:
        break
    

    if(state == 'R'):
        ed = time.time_ns() - st
        
        client_socket.send('1'.encode())
        print(ed)
        print('Message:', data.__sizeof__())
        
        state = 0
    

    elif(state == 0):
        if(data.decode() == 'Req Test'):
            print('<<Req Latency Test Start!>>')
            state = 'R'
        elif(data.decode() == 'Download Test'):
            print('<<Download Latency Test Start!>>')
            state = 'R'
        print('Received from Client:', addr, 'Message:', data.decode())
    
    
client_socket.close()
server_socket.close()
