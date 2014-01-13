######################################################################
# Fake Switch
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


import binascii, bitarray, dpkt, socket, sys, threading, time
import ofprotocol


class fakeSwitch(threading.Thread):
  """
  docstring
  """        
  def __init__(self): #now the initialization part of each thread
    threading.Thread.__init__(self) 
    """
    docstring
    """
    self.sleeptime = 0

  def run(self): #this is what is run when you do thread.start()
    if self.option == 1:
      self.packetInTest # method takes care of echo requests for keep alives
    elif self.option == 2:
      self.eatEcho()
    else:
      self.echo_loop()
      
  def setSleep(self, time):
    self.sleeptime = time

  def setOption(self, opt):
    self.option = opt

  def setConnection(self, connection):
    self.s = connection

  def open_TCP_Connection(self):
    host = '127.0.0.1'
    port = 6633
    self.s=socket.socket()
    self.s.connect((host,port))
    print("Established TCP Connection")

  def eatMessage(self):
    header = self.s.recv(8)
    #print repr(header)
    (version, msgtype, length, xid) = ofprotocol.deserializeHeader(header[:8])
    #print 'eatMessage: msgtype = ' + ofprotocol.messageTypeToString(msgtype) + '; length = ' + str(length)

    if (length > 8):
      body = self.s.recv(length - 8)
      #print(str(binascii.hexlify(body)))
      bodylen = str(binascii.hexlify(body)).__len__() #I bet there is an inherent way to call this

    if msgtype is ofprotocol.messageStringToType('HELLO'):
      self.s.send(ofprotocol.getHello(xid))

    elif msgtype is ofprotocol.messageStringToType('FEATURES_REQUEST'):
      #self.s.send(ofprotocol.getFeaturesReply(xid))
      self.s.send(bytearray.fromhex('010600b000000013000000000000000100000100ff000000000000c700000fff0002ae2082540a8c73312d657468320000000000000000000000000000000000000000c0000000000000000000000000fffe2ef2ce7647487331000000000000000000000000000000000001000000010000000000000000000000000000000000016e2f9006b5bb73312d657468310000000000000000000000000000000001000000c0000000000000000000000000'))

    elif msgtype is ofprotocol.messageStringToType('ECHO_REQUEST'):
      echo_reply_header = ofprotocol.getHeader(ofprotocol.messageStringToType['ECHO_REPLY'],
          length, xid)
      #print echo_reply_header.join(body)
      self.s.send(echo_reply_header.join(body))

    elif msgtype is ofprotocol.messageStringToType('SET_CONFIG'):
      print("set config") #no response needed, just need to eat additional message

    elif msgtype is ofprotocol.messageStringToType('GET_CONFIG_REQUEST'):
      msg = "0108000c" + str(xid) + "0000ffff"
      self.s.send(bytearray.fromhex(msg))

    elif msgtype is ofprotocol.messageStringToType('BARRIER_REQUEST'):
      reply = '011300080000' + body[bodylen-4:bodylen] #last 4 digits need to be the same from the barrier request
      self.s.send(bytearray.fromhex(reply))

    elif msgtype is ofprotocol.messageStringToType('FLOW_MOD'):
      msg = "011101ac" + str(xid) + "000400000003000000000000000000000000000200000000000000070000000000000094000000000000023e0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fffe00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
  
  def echo_loop(self):
    while(1):
      #time.sleep(self.sleeptime)
      self.s.send(bytearray.fromhex('0102000800000000'))
      #print("Sending Echo Reply")
      #self.eatMessage()

  def eatEcho(self):
    while(1):
      self.eatMessage()
      #print("in eat Echo")

  def packetInTest(self):
    while(1):
      self.s.send(bytearray.fromhex('010a006c0000000000000107005a000100003333000000166ae6be545fdd86dd6000000000240001fe8000000000000068e6befffe545fddff0200000000000000000000000000163a000502000001008f008abf0000000104000000ff0200000000000000000001ff545fdd'))
      #print("Sending  Second Packet In - Router Soliciation")
      self.s.recv(90) ## Packet Out (CSM) Respond

  def request_switch_neighbors(self):
    self.s.send(bytearray.fromhex('010a006c0000000000000100005a000200003333000000167a8ebe84fa1286dd600000000024000100000000000000000000000000000000ff0200000000000000000000000000163a000502000001008f0074f30000000104000000ff0200000000000000000001ff84fa12'))
    print("Sending  Packet In (AM) (108B) Multicast Listen Support Message V2")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received Packet Out Respond")
    #Packet Out message examples:
    #010d001800000017000001010002000800000008fffb0000
    #010d001800000018000001020001000800000008fffb0000
    #010d001800000019000001030002000800000008fffb0000
    self.s.send(bytearray.fromhex('010a00600000000000000101004e000200003333ff84fa127a8ebe84fa1286dd6000000000183aff00000000000000000000000000000000ff0200000000000000000001ff84fa128700516a00000000fe80000000000000788ebefffe84fa12'))
    print("Sending  Packet In - Neighbor Solicitation for fe80::....")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received Packet Out Respond")
    self.s.send(bytearray.fromhex('010a00600000000000000102004e000100003333ff545fdd6ae6be545fdd86dd6000000000183aff00000000000000000000000000000000ff0200000000000000000001ff545fdd870095dd00000000fe8000000000000068e6befffe545fdd'))
    print("Sending  Second Packet In - Neighbor Solicitation for fe80::....")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received Packet Out Respond")
    self.s.send(bytearray.fromhex('010c004000000000020000000000000000016e2f9006b5bb73312d657468310000000000000000000000000000000000000000c0000000000000000000000000'))
    print("Sending Port State (130B)")
    self.s.send(bytearray.fromhex('010a005800000000000001030046000200003333000000027a8ebe84fa1286dd6000000000103afffe80000000000000788ebefffe84fa12ff020000000000000000000000000002850018e20000000001017a8ebe84fa12'))
    print("Sending Packet In - Router Soliciation")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received First Packet Out Respond")
    self.s.send(bytearray.fromhex('010a005800000000000001040046000100003333000000026ae6be545fdd86dd6000000000103afffe8000000000000068e6befffe545fddff02000000000000000000000000000285006cfd0000000001016ae6be545fdd'))
    print("Sending Packet In - Router Soliciation")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received Second Packet Out Respond")
    self.s.send(bytearray.fromhex('010a006c0000000000000107005a000100003333000000166ae6be545fdd86dd6000000000240001fe8000000000000068e6befffe545fddff0200000000000000000000000000163a000502000001008f008abf0000000104000000ff0200000000000000000001ff545fdd'))
    print("Sending  Second Packet In - Router Soliciation")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received Third Packet Out Respond")

if __name__ == '__main__':
  """
  Create our fake switch
  """
  host = '127.0.0.1'
  port = 6633
  s=socket.socket()
  s.connect((host,port))
  print("Established TCP Connection")
  thread1 = fakeSwitch()
  thread1.setConnection(s)
  thread1.answer_initial_config_request() 
  thread1.setOption(0)
  thread1.start()
  thread2 = fakeSwitch()
  thread2.setConnection(s)
  thread2.setOption(2)
  #thread2.start()
