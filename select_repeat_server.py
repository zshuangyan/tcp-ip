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


stack = []
received = []
STACK_LIMIT = 4

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

        # 如果数据是期望数据或者期望数据为空, 则数据会直接上报
        print("stack before: %s" % stack)
        print("received before: %s" % received)
        if not nextseq or syn == nextseq:
            nextseq = syn + 1
            if stack:
                stack.pop(0)
                received.pop(0)
                for pos, flag in enumerate(received):
                    if flag == 0:
                        break
                stack[:] = stack[pos:]
                received[:] = received[pos:]
                nextseq = pos

        # 如果数据应该存放在当前栈中
        elif nextseq < syn < nextseq + STACK_LIMIT and received[syn-nextseq] == 0:
            if len(stack) > syn - nextseq:
                stack[syn-nextseq] = syn
                received[syn-nextseq] = 1
            else:
                for i in range(len(stack), syn-nextseq):
                    stack.append(0)
                    received.append(0)
                stack.append(syn-nextseq)
                received.append(1)

        print("stack after: %s" % stack)
        print("received after: %s" % received)


        # 模拟ACK响应无法到达对端
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
    time.sleep(0.5*random.random())
sock.close()
    
