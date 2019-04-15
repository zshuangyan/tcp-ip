import socket 
import time
import select
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.bind(("0.0.0.0", 8001))
now = time.time()
nextseq = None
while True:
    if time.time() - now > 300:
        break
    ready = select.select([sock], [], [], 0.3)
    if ready[0]:
        data, addr = sock.recvfrom(1024)
        print(data)
        syn = int(data.split(":")[-1])
        if nextseq is None or nextseq == syn:
            nextseq = syn + 1 
            ack = syn + 1
            if random.randint(1,5) == 1:
                content = "TIME: %s, ACK Failed: %s" % (time.time(), ack)
                print(content)
                print
            else:
                content = "TIME: %s, ACK: %s" % (time.time(), ack)
                print(content)
                print
                sock.sendto(content, addr)
    time.sleep(random.random())
sock.close()
    
