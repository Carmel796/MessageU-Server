import uuid
from protocol.constants import NAME_LEN, PUBKEY_LEN
from repositories.clients_repo import ClientsRepo

class BadInput(Exception): pass
class DuplicateUsername(Exception): pass
class NoSuchUser(Exception): pass

# Clients Service - Encapsulate direct DB queries for handlers to use

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
                print(f"commited new client to DB")
                return new_id
            except Exception:
                s.rollback()
                raise

    def list_clients_excluding(self, requester_id):
        with self.SessionLocal() as s:
            # auth gate: requester must exist
            if not ClientsRepo.get_by_id(s, requester_id):
                raise NoSuchUser("requester")

            # fetch (you can paginate/tune limit if needed)
            rows = ClientsRepo.list_page(s, limit=1000)
            return [(r.ID, r.UserName) for r in rows if r.ID != requester_id]

    def get_public_key(self, requester_id, tgt_id):
        with self.SessionLocal() as s:
            if not ClientsRepo.get_by_id(s, requester_id):
                raise NoSuchUser("requester")

            tgt_client = ClientsRepo.get_by_id(s, tgt_id)
            if not tgt_client:
                raise NoSuchUser("target")

            pubk = bytes(tgt_client.PublicKey)
            return pubk