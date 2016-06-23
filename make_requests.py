#!/bin/env python

# the initial bash:
'''
for i in {1..1000}
do
   nc localhost 6000 < file_list.txt
   if [ $? -ne 0 ]; then
      break
   fi
done
'''

import socket

def netcat(hostname, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.sendall(content)
    s.shutdown(socket.SHUT_WR)
    while 1:
        data = s.recv(1024)
        if data == '':
            break
        print("Received:", repr(data))
    print("Connection closed.")
    s.close()


def lines_in(f_name):
    with open(f_name,'r') as f:
        return f.read()



# initial try (no async):
def requests():
    for i in x.range(1000):
        netcat('localhost', 6000, lines_in('file_list.txt'))

if __name__ == '__main__':
    requests()

