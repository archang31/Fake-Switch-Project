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

class fakeSwitch(object):
    """
    docstring
    """        
    def __init__(self):
        """
        docstring
        """
        self.messageArray = []
        #self.buildMessageArray()
        self.handshake()
    
    def buildMessageArray(self):
        f = open("captures/mycap1211.pcap")
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in pcap: #ts = timestap, buf = packet
            eth = dpkt.ethernet.Ethernet(buf) # parse into ethernet
            ip = eth.data #parse into ip
            tcp = ip.data #parse into TCP
            print("from ", tcp.sport, binascii.hexlify(tcp.data))
            if str(tcp.dport) == "6633": #if it was outgoing TCP traffic
                self.messageArray.append(tcp.data) #add to the outgoing message array
    
    def handshake(self):
        host = '127.0.0.1'
        port = 6633
        msg_length = 12000
        print("Testing Handshake")
        self.s=socket.socket()
        self.s.connect((host,port))
        print("Established TCP Connection")
        msg = self.s.recv(74) ## Hello Message
        self.messageHandler(str(binascii.hexlify(msg)))
        msg = self.s.recv(74) ## Features Request
        self.messageHandler(str(binascii.hexlify(msg)))
        msg = self.s.recv(78) ## Set Config
        msg2 = self.s.recv(146) ## Barrier Request
        self.messageHandler(str(binascii.hexlify(msg2)))#must respond to barrier before config
        self.messageHandler(binascii.hexlify(msg))
        msg = self.s.recv(90) ## Packet Out (CSM)
        self.messageHandler(binascii.hexlify(msg))
        msg 
    
    def messageHandler(self, message):
        print(message, len(message))
        if len(message) == 16: #8B
            if message[0:12] == '010000080000':
                print("Received Hello SM")
                self.s.send(bytearray.fromhex('0100000800000002'))
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
            self.s.send(bytearray.fromhex('010a006c0000000000000100005a000200003333000000167a8ebe84fa1286dd600000000024000100000000000000000000000000000000ff0200000000000000000000000000163a000502000001008f0074f30000000104000000ff0200000000000000000001ff84fa12'))
            print("Sending  Packet In (AM) (108B) Multicast Listen Support Message V2")
        elif len(message) == 160:
            # example barrier:
            # ")#010e0048000000880010001f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000000008000ffffffffffff00000112000800000089
            print("Received Barrier Request (CSM) 8B")
            reply = '011300080000' + message[156:160]#last 4 digits need to be the same from the barrier message
            print(reply)
            self.s.send(bytearray.fromhex(reply))
            print("Sending  Barrier Reply (8B)")
                
        else:
            print("In else statement")

if __name__ == '__main__':
    """
    Create our fake switch
    """
    fakeSwitch()
