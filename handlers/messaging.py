# handlers/messaging.py
import struct
from protocol.constants import OK_SEND_MESSAGE, OK_PULL_WAITING   # define an opcode for success
from protocol.errors import error_response
from protocol.codec import build_response        # must frame (header+payload)
from services.message_service import MessageService, BadInput, NoSuchUser
from database.db import SessionLocal

HEADER_603_FMT = "<16sBI"   # target(16s), type(B), content_size(I)
HEADER_603_LEN = struct.calcsize(HEADER_603_FMT)
RESP_603_FMT = "<16sI"        # target(16s), msg_id(u32)

MSG_REC_HDR_FMT = "<16sIBI"
MSG_REC_HDR_LEN = struct.calcsize(MSG_REC_HDR_FMT)

def op603_send_message(sender_id: bytes, payload: bytes) -> bytes:
    # basic shape guard
    if len(payload) < HEADER_603_LEN:
        return error_response()

    target_id_b, msg_type, content_size = struct.unpack(HEADER_603_FMT, payload[:HEADER_603_LEN])
    content = payload[HEADER_603_LEN:]

    # length agreement
    if len(content) != content_size:
        return error_response()

    svc = MessageService(SessionLocal)
    try:
        msg_id = svc.send_message(from_client=sender_id,
                                  to_client=target_id_b,
                                  msg_type=msg_type,
                                  content=content)
    except (BadInput, NoSuchUser):
        return error_response()
    except Exception:
        return error_response()

    # success payload: return new message ID as u32 (fits your Message.ID constraint)
    payload_rsp = struct.pack(RESP_603_FMT, target_id_b, msg_id)
    return build_response(OK_SEND_MESSAGE, payload_rsp)

def op604_pull_waiting(sender_id: bytes, _payload) -> bytes:
    svc = MessageService(SessionLocal)
    try:
        rows = svc.pull_waiting(sender_id, limit=500, offset=0)
    except (NoSuchUser, Exception):
        return error_response()

    out = bytearray()
    for r in rows:
        from_id = bytes(r.FromClient)
        msg_id = int(r.ID)
        msg_type = int(r.Type) & 0xFF
        content = bytes(r.Content or b"")
        out += struct.pack(MSG_REC_HDR_FMT, from_id, msg_id, msg_type, len(content))
        out += content

    return build_response(OK_PULL_WAITING, bytes(out))