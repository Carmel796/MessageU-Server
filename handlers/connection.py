import socket
import struct

from protocol.constants import HEADER_SIZE, HEADER_FMT
from protocol.validators import validate_header, validate_payload
from protocol.errors import error_response
from router import dispatch

# Connection realted handlers

def read_exact(conn: socket.socket, n: int) -> bytes:
    """Read exactly n bytes from a blocking socket or raise ConnectionError on EOF."""
    if n == 0:
        return b""
    buf = bytearray(n)
    view = memoryview(buf)
    got = 0
    while got < n:
        nread = conn.recv_into(view[got:], n - got)
        if nread == 0:
            raise ConnectionError("peer closed during read")
        got += nread
    return bytes(buf)


def handle_request(conn, addr):
    try:
        while True:
            header = read_exact(conn, HEADER_SIZE)
            client_id, version, code, payload_size = struct.unpack(HEADER_FMT, header)

            err = validate_header(version, code, payload_size)
            if err:
                conn.sendall(error_response())
                break

            payload = read_exact(conn, payload_size) if payload_size else b""

            err = validate_payload(code, payload)
            if err:
                conn.sendall(error_response())
                break

            response = dispatch(client_id, code, payload)
            if response:
                conn.sendall(response)

    except (ConnectionError, socket.timeout):
            pass
    finally:
        conn.close()