from protocol.constants import NAME_LEN, PUBKEY_LEN, OK_REGISTER
from protocol.codec import build_response
from protocol.errors import error_response
from services.clients_service import ClientsService, BadInput, DuplicateUsername
from database.db import SessionLocal

# Registration related handlers

def op600_registration(_client_id, payload):
    name_bytes = payload[:NAME_LEN]
    pubk_bytes = payload[NAME_LEN:NAME_LEN + PUBKEY_LEN]

    svc = ClientsService(SessionLocal)
    try:
        new_id = svc.register(name_bytes, pubk_bytes)
    except (DuplicateUsername, BadInput, Exception):
        return error_response()

    return build_response(OK_REGISTER, new_id) # build_frame building response for GOOD response