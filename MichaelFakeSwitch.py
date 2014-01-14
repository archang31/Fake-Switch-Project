######################################################################
# Fake Switch
# Authors:
# Michael Kranch
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
    #self.open_TCP_Connection()
    #self.answer_initial_config_request() # method handles switch initial requests
    #self.request_switch_neighbors() Not needed for setup

  def run(self):
    if self.option == 1:
      self.packetInTest2 # method takes care of echo requests for keep alives
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
    #self.answer_initial_config_request()

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
      reply = '011300080000' + body[bodylen-4:bodylen] #last 4 digits need to be the same from the barrier request
      self.s.send(bytearray.fromhex(reply))

    elif msgtype is ofprotocol.messageStringToType('FLOW_MOD'):
      msg = "011101ac" + str(xid) + "000400000003000000000000000000000000000200000000000000070000000000000094000000000000023e0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fffe00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

  def answer_initial_config_request(self):
    self.eatMessage() ## Hello Message
    self.eatMessage() ## Features Request Message
    self.eatMessage() ## Set Config Message (no response needed)
    #Barrier Handling Not need for a ryu controller
    print("About to eat Barrier Message")
    msg2 = self.s.recv(146) ## Barrier Request
    msg2 = str(binascii.hexlify(msg2))
    reply = '011300080000' + msg2[len(msg2)-4:]#last 4 digits need to be the same from the barrier message
    self.s.send(bytearray.fromhex(reply))#Barrier Reply
    #self.eatMessage() #Get Config Request
    #self.s.send(bytearray.fromhex('0108000c010b5e800000ffff')) #Get Config Reply
  
  def echo_loop(self):
    while(1):
      time.sleep(1)
      self.s.send(bytearray.fromhex('0102000800000000'))
      print("Sending Echo Request")
      #self.eatMessage() #NOT WORKING FOR ECHO REPLY
      self.s.recv(74)
      self.packetInTest2()

  def eatEcho(self):
    while(1):
      time.sleep(.1)
      self.s.recv(74)
      #print("in eat Echo")

  def packetInTest(self):
      openheader = "010a007400000000" #01 Ver, 0a (10) is Packet IN Type, 0074 (116) is length, 00000000 is xid
      openpacket = "00000115" + "0062" + "0002" + "00" + "00" # Buffer ID (277) + Frame Length (98) + Recv Port (2) + Reason (No matching flow(0)) + Random "00"
      dstmac = "000000000001"
      srcmac = "000000000002"
      ethtype = "0800" #IP (0x0800)
      ethernet = dstmac + srcmac + ethtype
      srcip = "0a000002"
      dstip = "0a000001"
      IPV4 = "450000546431000040010276" + srcip + dstip
      control = "00005dd511ae0004083fd552bbe30c0008090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f3031323334353637"         
      frame = ethernet + IPV4 + control
      print(openheader + '\n' + openpacket + '\n' + ethernet + '\n' + IPV4)
      packet = openheader + openpacket + frame
      packet2 = "010a0074000000000000010d006200020000000000000001000000000002080045000054642f0000400102780a0000020a000001000044cd15880002f843d552e40e090008090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f3031323334353637"
      print(packet)
      print(packet2)
      self.s.send(bytearray.fromhex(packet))
      #print("Sending Second Packet In - Router Soliciation")
      self.s.recv(148) ## Packet Out (CSM) Respond

  def packetInTest2(self):
    packet2 = "010a003c0000000000000100002a000100" + "00"+ "00000000000100000000020806000108000604000200000000020a0000020000000000010a000001"
    arp = "0003000100060000000000010000080600010800060400020000000000010a0000010000000000020a000002"
    dstmac = "000000000001"
    srcmac = "000000000002"
    dstip = "0a000001"
    srcip = "0a000002"
    packet = "010a003c0000000000000100002a000100" + "00"+ dstmac + srcmac + "08060001080006040002" + srcmac + srcip + dstmac + dstip
    #arp = "000300010006000000000001000008060001080006040002" + srcmac + srcip + dstmac + dstip
    message = packet2# + arp
    #addressrequest = "010a003c0000000000000110002a00020000000000000001000000000002080600010800060400010000000000020a0000020000000000000a000001"
    dstmac = "000000000001"
    srcmac = "000000000002"
    unkmac = "000000000000"
    srcip = "0a000002"
    dstip = "0a000001"    
    frame = "08060001080006040001" + srcmac + srcip + unkmac + dstip
    recvport1 = "0009"
    recvport2 = "0008"
    addressrequest = "010a003c0000000000000110002a" + recvport1 + "0000" + dstmac + srcmac + frame
    self.s.send(bytearray.fromhex(addressrequest))
    self.s.recv(148) ## Flow Mod
    addressreply2 = "010a003c0000000000000111002a00010000000000000002000000000001080600010800060400020000000000010a0000010000000000020a000002"
    frame2 = "08060001080006040002" + dstmac + dstip + srcmac + srcip
    addressreply =   "010a003c0000000000000111002a" + recvport2 + "0000" + srcmac + dstmac + frame2
    print(addressreply)
    print(addressreply2)
    self.s.send(bytearray.fromhex(addressreply))
    self.s.recv(148) ## Flow Mod
    self.echo_loop()
    
  
  def request_switch_neighbors(self):
    self.s.send(bytearray.fromhex('010a006c0000000000000100005a000200003333000000167a8ebe84fa1286dd600000000024000100000000000000000000000000000000ff0200000000000000000000000000163a000502000001008f0074f30000000104000000ff0200000000000000000001ff84fa12'))
    print("Sending Packet In (AM) (108B) Multicast Listen Support Message V2")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received Packet Out Respond")
    #Packet Out message examples:
    #010d001800000017000001010002000800000008fffb0000
    #010d001800000018000001020001000800000008fffb0000
    #010d001800000019000001030002000800000008fffb0000
    self.s.send(bytearray.fromhex('010a00600000000000000101004e000200003333ff84fa127a8ebe84fa1286dd6000000000183aff00000000000000000000000000000000ff0200000000000000000001ff84fa128700516a00000000fe80000000000000788ebefffe84fa12'))
    print("Sending Packet In - Neighbor Solicitation for fe80::....")
    msg = self.s.recv(90) ## Packet Out (CSM) Respond
    print("Received Packet Out Respond")
    self.s.send(bytearray.fromhex('010a00600000000000000102004e000100003333ff545fdd6ae6be545fdd86dd6000000000183aff00000000000000000000000000000000ff0200000000000000000001ff545fdd870095dd00000000fe8000000000000068e6befffe545fdd'))
    print("Sending Second Packet In - Neighbor Solicitation for fe80::....")
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
    print("Sending Second Packet In - Router Soliciation")
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
  #thread2 = fakeSwitch()
  #thread2.setConnection(s)
  #thread2.setOption(0)
  #thread2.start()
