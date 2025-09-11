import uuid
from protocol.constants import NAME_LEN, PUBKEY_LEN
from repositories.clients_repo import ClientsRepo

class BadInput(Exception): pass
class DuplicateUsername(Exception): pass

class ClientsService:
    def __init__(self, SessionLocal):
        self.SessionLocal = SessionLocal

    def register(self, name_bytes, pubkey_bytes):
        name = name_bytes.rstrip(b"\x00").decode("utf-8", errors="ignore").strip()
        if not name or len(name.encode("utf-8")) > NAME_LEN:
            raise BadInput("invalid name")
        if len(pubkey_bytes) != PUBKEY_LEN:
            raise BadInput("invalid pubkey length")

        new_id = uuid.uuid4().bytes # 16 bytes

        with self.SessionLocal() as s:
            try:
                if ClientsRepo.get_by_username(s, name):
                    raise DuplicateUsername()
                ClientsRepo.insert(s, new_id, name, pubkey_bytes)
                s.commit()
                return new_id
            except Exception:
                s.rollback()
                raise