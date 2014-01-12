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
      thread = fakeSwitch.fakeSwitch()
      thread.setSleep(0)
      thread.setOption(0)
      thread.start()
      print("Starting Thread " + str(n))
      n = n + 1
  print("Done Loop")
