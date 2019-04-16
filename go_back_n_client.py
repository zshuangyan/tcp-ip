# -*- coding: UTF-8 -*-
import socket
import select
import time
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.connect(("0.0.0.0", 8001))
index = 0

data_base = 0

# stack用来保存已发送还未接收到确认的数据, STACK_LIMIT代表栈的长度
stack = []
STACK_LIMIT = 4

# now用于保证循环时间
now = time.time()

# timer是定时器, 用于超时重传, RETRANS代表超时时间, 以s为单位
timer = time.time()
RETRANS = 0.7

# 循环时间超过5min, 则跳出循环, 关闭sock
while time.time() - now < 300:

    # 使用非阻塞模式读取sock, 阻塞时间为0.3s
    ready = select.select([sock], [], [], 0.3)

    # 如果接收到对端响应
    if ready[0]:
        ACK = sock.recv(1024)

        # 获取响应中的ack
        ack = int(ACK.split(":")[-1])

        # 如果存在已发送但还未接收到确认的数据
        if stack:

            # 检查这些数据是否有匹配ack的
            try:
                pos = stack.index(ack-1)
            except ValueError:
                pass
            print("recv ack: %s" % ACK)
            print("stack before: %s" % stack)

            # 根据go-back-n算法特性, 匹配中的数据和它之前发送的数据, 都已经成功接收了
            stack[:] = stack[pos+1:]
            print("stack after: %s" % stack)

            # 如果有匹配中, 则重置定时器
            timer = time.time()
    else:
        # 如果定时器超时, 则重传最老的已发送但还未接收到确认的数据
        if time.time() - timer > RETRANS:
            content = "TIME: %s, RESEND SYN: %s" % (time.time(), stack[0])
            print(content)
            sock.send(content)
            # 重传后重置定时器以避免重复发送
            timer = time.time()

        # 如果从上层应用接收到数据, 并且存储已发送但还未接收到的数据栈还未满
        elif len(stack) != STACK_LIMIT:
            print("Add data to stack")
            print("stack before: %s" % stack)

            # 把数据加入到栈中, 数据是递增生成来模拟上层接收的数据
            stack.append(index)
            print("stack after: %s" % stack)
            index += 1 
            print("index is: %s" % index)
            print("TIME: %s, SYN: %s" % (time.time(), stack[-1]))
            sock.send("TIME: %s, SEND SYN: %s" % (time.time(), stack[-1]))

sock.close()
