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
        s=socket.socket()
        s.connect((host,port))
        print("Established TCP Connection")
        msg = s.recv(74) ## s.recv in bytes
        print("received " + binascii.hexlify(msg))
        print("sending  " + "0100000800000002")
        s.send(bytearray.fromhex('0100000800000002'))
        msg = s.recv(74) ## s.recv in bytes
        print("received " + binascii.hexlify(msg))
        msg = binascii.hexlify(msg)
        #outgoing = '01050008000000'
        #outgoing = outgoing + msg[14:15]
        #print(outgoing)
        print("sending  " + "010600b000000013000000000000000100000100ff000000000000c700000fff0002ae2082540a8c73312d657468320000000000000000000000000000000000000000c0000000000000000000000000fffe2ef2ce7647487331000000000000000000000000000000000001000000010000000000000000000000000000000000016e2f9006b5bb73312d657468310000000000000000000000000000000001000000c0000000000000000000000000")
        s.send(bytearray.fromhex('010600b000000013000000000000000100000100ff000000000000c700000fff0002ae2082540a8c73312d657468320000000000000000000000000000000000000000c0000000000000000000000000fffe2ef2ce7647487331000000000000000000000000000000000001000000010000000000000000000000000000000000016e2f9006b5bb73312d657468310000000000000000000000000000000001000000c0000000000000000000000000'))
        msg = s.recv(74) ## s.recv in bytes
        print("received " + binascii.hexlify(msg))

if __name__ == '__main__':
    """
    Create our fake switch
    """
    fakeSwitch()
