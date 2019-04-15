import socket
import select
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.connect(("0.0.0.0", 8001))
index = 0
for i in range(10):
    content = "TIME: %s, SYN: %s" % (time.time(), index)
    sock.send(content)
    ready = select.select([sock], [], [], 1)
    if ready[0]:
        ACK = sock.recv(1024)
        ack = int(ACK.split(":")[-1])
        if ack != index + 1:
            continue
        print("%s %s" % (content, ACK))
        index += 1
sock.close()

