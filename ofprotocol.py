import struct

message_type_str_indexed = {'HELLO':0, 'ERROR':1, 'ECHO_REQUEST':2, 'ECHO_REPLY':3,
	'VENDOR':4, 'FEATURES_REQUEST':5, 'FEATURES_REPLY':6,
	'GET_CONFIG_REQUEST':7, 'GET_CONFIG_REPLY':8 }
message_type_int_indexed = {v:k for k, v in message_type_str_indexed.items()}

def messageTypeToString(typeint):
	return message_type_int_indexed[typeint]

def messageStringToType(typestr):
	return message_type_str_indexed[typestr]

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
	version = 0x01
	xid = 0x01
	packet = struct.pack('!BBHI', version, msgtype, length, xid)
	# packet = struct.pack('<IHBB', xid, length, msgtype, version)
	#print len(packet)
	return packet

def deserializeHeader(header):
	packet = struct.unpack('!BBHI', header)
	(version, msgtype, length, xid) = packet
	return packet

def getHello():
	helloType = 0x00
	headerLen = 0x08
	return getHeader(helloType, headerLen)
