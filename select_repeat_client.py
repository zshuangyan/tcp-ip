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

# stack用于存储已发送的数据
stack = []
# not_acked用于存储stack中还未确认的数据的索引
not_acked = []
STACK_LIMIT = 4

# now用于保证循环时间
now = time.time()

# timer是定时器, 用于超时重传, RETRANS代表超时时间, 以s为单位
timer = time.time()
RETRANS = 0.8

# 循环时间超过5min, 则跳出循环, 关闭sock
while time.time() - now < 300:

    # 使用非阻塞模式读取sock, 阻塞时间为0.3s
    ready = select.select([sock], [], [], 0.3)

    # 如果接收到对端响应
    if ready[0]:
        ACK = sock.recv(1024)

        # 获取响应中的ack
        ack = int(ACK.split(":")[-1])

        # 如果stack不为空
        if stack:

            # 检查这些数据是否有匹配ack的
            try:
                pos = stack.index(ack-1)
            except ValueError:
                pass
            else:
    
                # 如果被匹配中的是栈中的首位
                print("recv ack: %s" % ACK)
                print("stack before: %s" % stack)
                print("not acked before: %s" % not_acked)
                if pos == 0:
                    not_acked.pop(0)
                    if len(not_acked) >= 1:
                        next_not_ack = not_acked[0]
                        stack[:] = stack[next_not_ack:]
                        not_acked = [pos-next_not_ack for pos in not_acked]
                    else:
                        stack = []
                    # 如果匹配中的是栈的首位, 则重置定时器
                    timer = time.time()
                # 如果被匹配中的是栈的其他位置
                else:
                    try:
                        not_acked.remove(pos)
                    except ValueError:
                        pass
                print("stack after: %s" % stack)
                print("not acked after: %s" % not_acked)
                print

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
            print("Add data: %s to stack" % index)
            print("stack before: %s" % stack)
            print("not acked before: %s" % not_acked)

            # 把数据加入到栈中, 数据是递增生成来模拟上层接收的数据
            stack.append(index)
            not_acked.append(len(stack)-1)
            print("stack after: %s" % stack)
            print("not acked after: %s" % not_acked)
            print
            index += 1 
            print("TIME: %s, SYN: %s" % (time.time(), stack[-1]))
            print
            sock.send("TIME: %s, SEND SYN: %s" % (time.time(), stack[-1]))

sock.close()
