######################################################################
# Multiple Switch Test
# Authors:  
#           Michael Kranch
#
# Python 3.3.2
#
# Description:
#
#
#
######################################################################

import socket
import sys
import dpkt
import binascii
import bitarray
import time
import ofprotocol
import threading
import fakeSwitch

if __name__ == '__main__':
  """
  Start our thread test
  """
  n = 0
  while n < 10:
    host = '127.0.0.1'
    port = 6633
    s=socket.socket()
    s.connect((host,port))
    thread1 = fakeSwitch.fakeSwitch()
    thread1.setConnection(s)
    thread1.answer_initial_config_request() 
    thread1.setOption(0)
    thread1.start()
    thread2 = fakeSwitch.fakeSwitch()
    thread2.setConnection(s)
    thread2.setOption(2)
    thread2.start()
    print("Starting Thread " + str(n))
    n = n + 1
  print("Done Loop")
