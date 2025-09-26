# services/messages_service.py
from dataclasses import dataclass
from typing import Iterable
from repositories.messages_repo import MessagesRepo
from repositories.clients_repo import ClientsRepo
from sqlalchemy.orm import Session
from db import SessionLocal

class BadInput(Exception): pass
class NoSuchUser(Exception): pass

MAX_CONTENT = 1_000_000  # safety cap; tune as you like

@dataclass
class MessageService:
    SessionLocal: callable = SessionLocal  # inject for testability

    def send_message(self, from_client: bytes, to_client: bytes, msg_type: int, content: bytes) -> int:
        if not isinstance(msg_type, int) or not (0 <= msg_type <= 255):
            raise BadInput("invalid message type")
        if not isinstance(content, (bytes, bytearray)):
            raise BadInput("content must be bytes")
        if len(content) > MAX_CONTENT:
            raise BadInput("content too large")

        with self.SessionLocal() as s:
            try:
                # auth/existence checks
                if not ClientsRepo.get_by_id(s, from_client):
                    raise NoSuchUser("sender")
                if not ClientsRepo.get_by_id(s, to_client):
                    raise NoSuchUser("target")

                row = MessagesRepo.insert(s, to_client=to_client, from_client=from_client,
                                          msg_type=msg_type, content=bytes(content))
                s.commit()
                return int(row.ID)
            except Exception:
                s.rollback()
                raise

    def list_for_client(self, client_id: bytes, *, limit: int = 500, offset: int = 0):
        with self.SessionLocal() as s:
            if not ClientsRepo.get_by_id(s, client_id):
                raise NoSuchUser("requester")
            return MessagesRepo.list_for_client(s, client_id, limit=limit, offset=offset)
