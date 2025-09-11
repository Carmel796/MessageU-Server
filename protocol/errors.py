# protocol/errors.py
from protocol.codec import build_response
from protocol.constants import ERROR_CODE

def error_response():
    return build_response(ERROR_CODE, b"")  # size = 0, no payload
