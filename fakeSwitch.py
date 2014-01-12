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


import socket
import sys
import dpkt
import binascii
import bitarray
import time
import ofprotocol
import threading

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
    self.open_TCP_Connection()
    self.answer_initial_config_request() # method handles switch initial requests
    #self.request_switch_neighbors() Not needed for setup

  def run(self):
    if self.option == 1:
      self.packetInTest # method takes care of echo requests for keep alives
    else:
      self.echo_loop()
      
  def setSleep(self, time):
    self.sleeptime = time

  def setOption(self, opt):
    self.option = opt

  def open_TCP_Connection(self):
    host = '127.0.0.1'
    port = 6633
    self.s=socket.socket()
    self.s.connect((host,port))
    print("Established TCP Connection")

  def eatMessage(self):
    header = self.s.recv(8)
    print repr(header)
    (version, msgtype, length, xid) = ofprotocol.deserializeHeader(header[:8])
    print 'eatMessage: msgtype = ' + ofprotocol.messageTypeToString(msgtype) + '; length = ' + str(length)

    body = None
    if (length > 8):
      body = self.s.recv(length - 8)
      #print(str(binascii.hexlify(body)))
      bodylen = str(binascii.hexlify(body)).__len__() #I bet there is an inherent way to call this

    if msgtype is ofprotocol.messageStringToType('HELLO'):
      self.s.send(ofprotocol.getHello(xid))

    elif msgtype is ofprotocol.messageStringToType('FEATURES_REQUEST'):
      self.s.send(ofprotocol.getFeaturesReply(xid))

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
      reply = '011300080000'
      if body:
        reply = reply + body[bodylen-4:bodylen] #last 4 digits need to be the same from the barrier request
      self.s.send(bytearray.fromhex(reply))

    elif msgtype is ofprotocol.messageStringToType('FLOW_MOD'):
      msg = "011101ac" + str(xid) + "000400000003000000000000000000000000000200000000000000070000000000000094000000000000023e0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fffe00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

  def answer_initial_config_request(self):
    self.eatMessage() ## Hello Message
    self.eatMessage() ## Features Request Message
    self.eatMessage() ## Set Config Message (no response needed)
    #self.eatMessage() ## Flow Mod Request
    #self.eatMessage() ## Barrier Request
    #not sure why I could not get your barrier request to be right so I just went back to using my default.
    #your eatMessage actually makes it look like its a Flow Mod Request with lenght 72 followed by a Barrier Request when,
    #according to wireshark, its just a barrier Request after the set config message.
    #msg2 = self.s.recv(146) ## Barrier Request
    #this message is not needed for a ryu controller
    #self.messageHandler(msg2) ## Barrier Reply
    self.eatMessage() #Get Config Request
    #self.s.send(bytearray.fromhex('0108000c010b5e800000ffff')) #Get Config Reply
    #real switch reply Header = 01 08 00 0c
    #second byte is "transaction ID "00 b6  8c 98 ''    00 00 ff ff 

    #this message is not sent on a ryu controller
    
 #   msg = self.s.recv(74) ## Hello Message
 #   self.genericMessageHandler(msg)
 
    #self.messageHandler(msg)
 #   msg = self.s.recv(74) ## Features Request
 #   self.genericMessageHandler(msg)
    #self.messageHandler(msg)
 #   msg = self.s.recv(78) ## Set Config Message (no response needed)
    # msg2 = self.s.recv(146) ## Barrier Request
    # self.messageHandler(msg2) ## Barrier Reply
  
  def echo_loop(self):
    while(1):
      time.sleep(self.sleeptime)
      self.s.send(bytearray.fromhex('0102000800000000'))
      #print("Sending Echo Reply")
      self.eatMessage()

  def packetInTest(self):
    while(1):
      self.s.send(bytearray.fromhex('010a006c0000000000000107005a000100003333000000166ae6be545fdd86dd6000000000240001fe8000000000000068e6befffe545fddff0200000000000000000000000000163a000502000001008f008abf0000000104000000ff0200000000000000000001ff545fdd'))
      #print("Sending  Second Packet In - Router Soliciation")
      self.s.recv(90) ## Packet Out (CSM) Respond
      
  def messageHandler(self, msg):
    message = str(binascii.hexlify(msg))
    #print(message, len(message))
    #print msg, len(msg)
    header = ofprotocol.deserializeHeader(msg[:8])
    (version, msgtype, length, xid) = header
    #print 'messageHandler: deserializeHeader: ' + str(header)

    if len(message) == 16: #8B

      if message[0:12] == '010000080000':
        print("Received Hello SM")
        self.s.send(ofprotocol.getHello())
        #self.s.send(bytearray.fromhex('0100000800000002'))
        print("Sending  Hello SM (8B)")

      elif message[0:12] == '010500080000':
        print("Received Features Request (SM)")
        self.s.send(bytearray.fromhex('010600b000000013000000000000000100000100ff000000000000c700000fff0002ae2082540a8c73312d657468320000000000000000000000000000000000000000c0000000000000000000000000fffe2ef2ce7647487331000000000000000000000000000000000001000000010000000000000000000000000000000000016e2f9006b5bb73312d657468310000000000000000000000000000000001000000c0000000000000000000000000'))
        print("Sending  Features Reply (176B)")

      else:
        print("ERROR: IN ELSE FOR LENGTH 16")

    elif len(message) == 24:
      #if message[0:14] == '0109000c000000' and message[16:24] == '00000080':
          #three messages 0109000c0000006e00000080
          #               0109000c0000007300000080
          #               0109000c0000007800000080
      print("Set Config (CSM) (12B)")
      print("I do not believe a response is needed")

    elif len(message) == 160:
      # example barrier:
      # ")#010e0048000000880010001f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000008000ffffffffffff00000112000800000089
      print("Received Barrier Request (CSM) 8B")
      reply = '011300080000' + message[156:160]#last 4 digits need to be the same from the barrier message
      self.s.send(bytearray.fromhex(reply))
      print("Sending  Barrier Reply (8B)")
            
    else:
      print("In else statement from message handler - should not be here")

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
  thread1 = fakeSwitch()
  thread1.setSleep(2)
  thread1.setOption(0)
  thread1.start()

