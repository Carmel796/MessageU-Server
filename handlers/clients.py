from services.clients_service import ClientsService, NoSuchUser
from protocol.constants import OK_LIST_CLIENTS, NAME_LEN
from protocol.errors import error_response
from protocol.codec import build_response
from db import SessionLocal

def _name_to_255(name_str: str) -> bytes:
    b = name_str.encode("utf-8")
    if len(b) > NAME_LEN:
        b = b[:NAME_LEN]                   # should not happen if 600 validated, but safe
    return b + (b"\x00" * (NAME_LEN - len(b)))

def op601_list_clients(client_id, _payload):
    svc = ClientsService(SessionLocal)

    try:
        rows = svc.list_clients_excluding(client_id)
    except (NoSuchUser, Exception):
        return error_response()

    payload = bytearray()
    for cid, name in rows:
        payload += cid
        payload += _name_to_255(name)

    return build_response(OK_LIST_CLIENTS, bytes(payload))