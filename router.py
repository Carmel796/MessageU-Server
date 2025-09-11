from protocol.errors import error_response
from handlers.registration import op600_registration
# from handlers.clients      import op601_list_clients, op602_get_pubkey
# from handlers.messaging    import op603_send_message, op604_pull_waiting

HANDLERS = {
    600: op600_registration,
    # 601: op601_list_clients,
    # 602: op602_get_pubkey,
    # 603: op603_send_message,
    # 604: op604_pull_waiting,
}

def dispatch(client_id: bytes, code: int, payload: bytes) -> bytes:
    fn = HANDLERS.get(code)
    if not fn:
        return error_response()
    return fn(client_id, payload)
