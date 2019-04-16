# -*- coding: UTF-8 -*-
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
    # 循环时间超过5min, 则跳出循环, 关闭sock
    if time.time() - now > 300:
        break

    # 使用非阻塞模式读取sock, 等待时间为0.3s
    ready = select.select([sock], [], [], 0.3)
    if ready[0]:
        data, addr = sock.recvfrom(1024)
        print(data)
        syn = int(data.split(":")[-1])

        # 如果接收到的syn是期望的下一个数据, 则nextseq递增
        if nextseq is None or nextseq == syn:
            nextseq = syn + 1 
          

        # 模拟ACK响应无法到达对端
        if random.randint(1,5) == 1:
            content = "TIME: %s, ACK Failed: %s" % (time.time(), nextseq)
            print(content)
            print
        else:
            content = "TIME: %s, ACK: %s" % (time.time(), nextseq)
            print(content)
            print
            sock.sendto(content, addr)
    time.sleep(random.random())
sock.close()
    
