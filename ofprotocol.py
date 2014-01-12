import struct

message_type_str_indexed = {'HELLO':0, 'ERROR':1, 'ECHO_REQUEST':2, 'ECHO_REPLY':3,
	'VENDOR':4, 'FEATURES_REQUEST':5, 'FEATURES_REPLY':6,
	'GET_CONFIG_REQUEST':7, 'GET_CONFIG_REPLY':8,
	'SET_CONFIG': 9, 'PACKET_IN': 10, 'FLOW_REMOVED': 11, 'PORT_STATUS':12,
	'PACKET_OUT':13, 'FLOW_MOD': 14, 'PORT_MOD': 15, 'STATS_REQUEST':16,
	'STATS_REPLY':17, 'BARRIER_REQUEST':18, 'BARRIER_REPLY':19}
	
message_type_int_indexed = {v:k for k, v in message_type_str_indexed.items()}

def messageTypeToString(typeint):
	return message_type_int_indexed[typeint]

def messageStringToType(typestr):
	return message_type_str_indexed[typestr]

def isHelloType(type):
	return type is message_type_str_indexed['HELLO']

def getHeader(msgtype, length, xid):
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
	packet = struct.pack('!BBHI', version, msgtype, length, xid)
	# packet = struct.pack('<IHBB', xid, length, msgtype, version)
	#print len(packet)
	return packet

def deserializeHeader(header):
	packet = struct.unpack('!BBHI', header)
	(version, msgtype, length, xid) = packet
	return packet

def getHello(xid):
	helloType = message_type_str_indexed['HELLO']
	headerLen = 0x08
	return getHeader(helloType, headerLen, xid)

def getFeaturesReply(xid):
	'''/* Switch features. */

	struct ofp_switch_features {
		struct ofp_header header;
		uint64_t datapath_id; /* Datapath unique ID. The lower 48-bits are for a MAC address, while the upper 16-bits are implementer-defined. */
		uint32_t n_buffers; /* Max packets buffered at once. */
		uint8_t n_tables; /* Number of tables supported by datapath. */
		uint8_t pad[3]; /* Align to 64-bits. */

		/* Features. */
		uint32_t capabilities; /* Bitmap of support "ofp_capabilities". */
		uint32_t actions; /* Bitmap of supported "ofp_action_type"s. */

		/* Port info.*/
		struct ofp_phy_port ports[0]; /* Port definitions. The number of ports is inferred from the length field in the header. */
	};

	OFP_ASSERT(sizeof(struct ofp_switch_features) == 32);'''

	# temporarily just hardcode it
	return bytearray.fromhex('00000304000600000000000000000800450000e4f48f4000400647827f0000017f0000018e8119e94cf23352dc6797c980180201fed800000101080a0007c7c10007c7c1010600b000000001000000000000000100000100ff000000000000c700000fff000202595b0b1f5373312d657468320000000000000000000000000000000000000000c0000000000000000000000000fffede81968d4544733100000000000000000000000000000000000100000001000000000000000000000000000000000001de24905e3f8c73312d657468310000000000000000000000000000000001000000c0000000000000000000000000')
	#return bytearray.fromhex('010600b000000013000000000000000100000100ff000000000000c700000fff0002ae2082540a8c73312d657468320000000000000000000000000000000000000000c0000000000000000000000000fffe2ef2ce7647487331000000000000000000000000000000000001000000010000000000000000000000000000000000016e2f9006b5bb73312d657468310000000000000000000000000000000001000000c0000000000000000000000000')
