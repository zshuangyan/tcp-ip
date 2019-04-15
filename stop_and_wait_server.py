import socket 
import time
import select

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.bind(("0.0.0.0", 8001))
now = time.time()
while True:
    if time.time() - now > 300:
        break
    ready = select.select([sock], [], [], 1)
    if ready[0]:
        data, addr = sock.recvfrom(1024)
        print(data)
        syn = int(data.split(":")[-1])
        if syn == 3:
            time.sleep(1.2) 
        ack = syn + 1
        sock.sendto("TIME: %s, ACK: %s" % (time.time(), ack), addr)
sock.close()
    
