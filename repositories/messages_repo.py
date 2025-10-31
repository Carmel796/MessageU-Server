# repositories/messages_repo.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models import Message  # your ORM model

class MessagesRepo:
    @staticmethod
    def insert(s: Session, to_client: bytes, from_client: bytes, msg_type: int, content: bytes) -> Message:
        row = Message(ToClient=to_client, FromClient=from_client, Type=msg_type, Content=content)
        s.add(row)
        s.flush()             # populate row.ID (auto-increment) before commit
        return row

    @staticmethod
    def get_client_messages(s: Session, client_id: bytes, limit: int = 500, offset: int = 0) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.ToClient == client_id)
            .order_by(Message.ID.asc())
            .limit(limit).offset(offset)
        )
        return list(s.execute(stmt).scalars().all())

    @staticmethod
    def get_by_id(s: Session, msg_id: int) -> Optional[Message]:
        return s.get(Message, msg_id)
