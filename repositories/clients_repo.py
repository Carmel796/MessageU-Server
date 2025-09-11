# app/repositories/clients_repo.py
from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from models import Client  # or: from app.models import Client

class ClientsRepo:
    @staticmethod
    def get_by_id(s: Session, client_id: bytes) -> Optional[Client]:
        return s.get(Client, client_id)

    @staticmethod
    def get_by_username(s: Session, username: str) -> Optional[Client]:
        stmt = select(Client).where(Client.UserName == username)
        return s.execute(stmt).scalar_one_or_none()

    @staticmethod
    def insert(s: Session, client_id: bytes, username: str, public_key: bytes) -> Client:
        row = Client(ID=client_id, UserName=username, PublicKey=public_key)
        s.add(row)          # no commit here; service will commit
        return row

    @staticmethod
    def list_page(s: Session, limit: int = 500, offset: int = 0) -> List[Client]:
        stmt = (
            select(Client)
            .order_by(Client.UserName.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(s.execute(stmt).scalars().all())

    @staticmethod
    def touch_last_seen(s: Session, client_id: bytes, when: datetime) -> int:
        stmt = update(Client).where(Client.ID == client_id).values(LastSeen=when)
        res = s.execute(stmt)
        return res.rowcount or 0
