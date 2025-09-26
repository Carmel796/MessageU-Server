# handlers/messaging.py
import struct
from protocol.constants import OK_SEND_MESSAGE   # define an opcode for success
from protocol.errors import error_response
from protocol.codec import build_response        # must frame (header+payload)
from services.message_service import MessageService, BadInput, NoSuchUser
from db import SessionLocal

HEADER_603_FMT = "<16sBI"   # target(16s), type(B), content_size(I)
HEADER_603_LEN = struct.calcsize(HEADER_603_FMT)
RESP_603_FMT = "<16sI"        # target(16s), msg_id(u32)


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
