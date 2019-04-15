import socket
import select
import time
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.connect(("0.0.0.0", 8001))
index = 0

data_base = 0
stack = []
STACK_LIMIT = 4
now = time.time()
timer = time.time()
RETRANS = 1
while time.time() - now < 300:
    ready = select.select([sock], [], [], 0.3)
    if ready[0]:
        ACK = sock.recv(1024)
        ack = int(ACK.split(":")[-1])
        if stack:
            try:
                pos = stack.index(ack-1)
            except ValueError:
                pass
            print("recv ack: %s" % ACK)
            print("stack before: %s" % stack)
            stack[:] = stack[pos+1:]
            print("stack after: %s" % stack)
            timer = time.time()
    else:
        if time.time() - timer > RETRANS:
            content = "TIME: %s, RESEND SYN: %s" % (time.time(), stack[0])
            print(content)
            sock.send(content)
            timer = time.time()
        elif len(stack) != STACK_LIMIT:
            print("Add data to stack")
            print("stack before: %s" % stack)
            stack.append(index)
            print("stack after: %s" % stack)
            index += 1 
            print("index is: %s" % index)
            print("TIME: %s, SYN: %s" % (time.time(), stack[-1]))
            sock.send("TIME: %s, SEND SYN: %s" % (time.time(), stack[-1]))

sock.close()
