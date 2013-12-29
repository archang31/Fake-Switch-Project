import struct

def getHeader(msgtype, length):
	'''Header on all OpenFlow packets.

	struct ofp_header {
		uint8_t version;
		uint8_t type;
		uint16_t length;
		uint32_t xid;
	};
	OFP_ASSERT(sizeof(struct ofp_header) == 8);

	'''
	version = 0x02
	xid = 0x01
	# packet = struct.pack('!BBHI', version, msgtype, length, xid)
	packet = struct.pack('<IHBB', xid, length, msgtype, version)
	print len(packet)
	return packet

def deserializeHeader(header):
	packet = struct.unpack('<IHBB', header)
	print packet

def getHello():
	helloType = 0x00
	headerLen = 0x08
	return getHeader(helloType, headerLen)