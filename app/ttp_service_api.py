# !/usr/bin/env python
# _*_coding:utf-8_*_

# 客戶端 ，用來呼叫service_Server.py
import socket
import sys
import struct


### Don't touch
def askForService(token, data):
	# HOST, PORT 記得修改
	global HOST
	global PORT
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	received = ""
	try:
		sock.connect((HOST, PORT))
		msg = bytes(token + "@@@" + data, "utf-8")
		msg = struct.pack(">I", len(msg)) + msg
		sock.sendall(msg)
		received = str(sock.recv(8192), "utf-8")
	finally:
		sock.close()
	return received


### Don't touch

def process(data):
    token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ3bW1rcy5jc2llLmVkdS50dyIsInNlcnZpY2VfaWQiOiIxNyIsIm5iZiI6MTU4MTY3MTM0Niwic2NvcGVzIjoiMCIsInVzZXJfaWQiOiI4NSIsImlzcyI6IkpXVCIsInZlciI6MC4xLCJpYXQiOjE1ODE2NzEzNDYsInN1YiI6IiIsImlkIjoyNjQsImV4cCI6MTczOTM1MTM0Nn0.SLC2x7zekyuBu9MVPeGUTCeLyYY_z-d8r8iPgE_cGpO7f8SIEnkv0XqGxw7iJPj8BJikVqr0uHjTXzkdxyv8XhLpHaeKFFlQjmiNtZ0BgmDkuiFOVmLYZtsML4qWCbZmXd7VgBuMPtZzLL0LuPoRjSPEe4bV8Z6DUsyXntPZnjc"
	# 可在此做預處理
	
	# 送出
    result = askForService(token, data)
	# 可在此做後處理
	
    return result


global HOST
global PORT
HOST, PORT = "140.116.245.149", 27005
if __name__ == "__main__":
	data = "烘碗機"
	# for i in range(1): print("Client : ", process(token, data))
	print(process(data))