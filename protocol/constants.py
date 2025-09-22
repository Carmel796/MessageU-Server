import struct

# app/protocol/constants.py
VERSION = 2

# lengths
ID_LEN = 16
NAME_LEN = 255
PUBKEY_LEN = 160

# request opcodes (for reference)
OP_REGISTER      = 600
OP_LIST_CLIENTS  = 601
OP_GET_PUBKEY    = 602
OP_SEND_MESSAGE  = 603
OP_PULL_WAITING  = 604

# response success codes
OK_REGISTER      = 2100  # payload: ClientID(16)
OK_LIST_CLIENTS  = 2101  # payload: repeated [ClientID(16)+Name(255)]
OK_GET_PUBKEY    = 2102  # payload: ClientID(16)+PublicKey(160)
OK_SEND_MESSAGE  = 2103  # payload: TargetID(16)+MessageID(4)
OK_PULL_WAITING  = 2104  # payload: repeated [FromID(16)+MsgID(4)+Type(1)+Size(4)+Content(N)]

# single global error response
ERROR_CODE = 9000  # payload size = 0

# protocol
HEADER_FMT = "<16sBHI"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
