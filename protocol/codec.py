import struct
from protocol.constants import VERSION


# Responses (server -> client)
RESP_HEADER_FMT = "<BHI"     # Version(1) | Code(2) | PayloadSize(4)

def build_response(code: int, payload: bytes, version: int = VERSION) -> bytes:
    """Build server->client frame: Version | Code | PayloadSize | Payload (little-endian)."""
    header = struct.pack(RESP_HEADER_FMT, version, code, len(payload))
    return header + payload