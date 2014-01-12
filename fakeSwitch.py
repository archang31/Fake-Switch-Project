######################################################################
# Fake Switch
# Authors:  
#           Michael Kranch, Bonnie Eisenman
#
# Description:
#
######################################################################


import binascii, bitarray, dpkt, socket, sys, threading, time
import ofprotocol

class fakeSwitch():
  """
  docstring
  """        
  def __init__(self): #now the initialization part of each thread
    """
    docstring
    """
    self.sleeptime = 0
    self.open_TCP_Connection()

    while True:
      time.sleep(2)
      self.eatMessage()

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

    if len(header) != 8:
      print 'wrong length!'
      return

    (version, msgtype, length, xid) = ofprotocol.deserializeHeader(header[:8])
    print 'eatMessage: msgtype = ' + ofprotocol.messageTypeToString(msgtype) + '; length = ' + str(length)

    body = None
    if (length > 8):
      body = self.s.recv(length - 8)
      bodylen = len(str(binascii.hexlify(body)))
      print body

    reply = None

    if msgtype is ofprotocol.messageStringToType('HELLO'):
      reply = ofprotocol.getHello(xid)

    elif msgtype is ofprotocol.messageStringToType('FEATURES_REQUEST'):
      reply = ofprotocol.getFeaturesReply(xid)

    elif msgtype is ofprotocol.messageStringToType('ECHO_REQUEST'):
      echo_reply_header = ofprotocol.getHeader(ofprotocol.messageStringToType['ECHO_REPLY'],
          length, xid)
      reply = echo_reply_header.join(body)

    elif msgtype is ofprotocol.messageStringToType('SET_CONFIG'):
      print("set config") #no response needed, just need to eat additional message

    elif msgtype is ofprotocol.messageStringToType('GET_CONFIG_REQUEST'):
      msg = "0108000c" + str(xid) + "0000ffff"
      reply = bytearray.fromhex(msg)

    elif msgtype is ofprotocol.messageStringToType('BARRIER_REQUEST'):
      r = '011300080000'
      if body:
        r = r + body[bodylen-4:bodylen] #last 4 digits need to be the same from the barrier request
      reply = bytearray.fromhex(r)

    elif msgtype is ofprotocol.messageStringToType('FLOW_MOD'):
      msg = "011101ac" + str(xid) + "000400000003000000000000000000000000000200000000000000070000000000000094000000000000023e0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000fffe00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000003000000000000000600000000000000ee00000000000001e400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

    if reply:
      print 'Sending reply: ', repr(reply)
      self.s.send(reply)

  
  def echo_loop(self):
    print 'echo_loop'
    while(1):
      time.sleep(self.sleeptime)
      self.s.send(bytearray.fromhex('0102000800000000'))
      #print("Sending Echo Reply") <-- is that a request?
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
  fs = fakeSwitch()
  #thread = threading.Thread(target=fs.echo_loop,args=())
  #thread.start()
  # thread1.setSleep(2)
  # thread1.setOption(0)
  # thread1.start()

