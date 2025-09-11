# models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BLOB, TEXT, DATETIME, Integer, CheckConstraint, ForeignKey

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = "clients"
    ID: Mapped[bytes]        = mapped_column(BLOB, primary_key=True)
    UserName: Mapped[str]    = mapped_column(TEXT, unique=True, nullable=False)
    PublicKey: Mapped[bytes] = mapped_column(BLOB, unique=True, nullable=False)
    LastSeen: Mapped[str | None] = mapped_column(DATETIME)

    __table_args__ = (
        CheckConstraint("length(ID)=16", name="ck_clients_id_16"),
        CheckConstraint("length(UserName)<=255", name="ck_clients_username_255"),
        CheckConstraint("length(PublicKey)=160", name="ck_clients_pubkey_160"),
    )

class Message(Base):
    __tablename__ = "messages"
    ID: Mapped[int]          = mapped_column(Integer, primary_key=True)
    ToClient: Mapped[bytes]  = mapped_column(BLOB, ForeignKey("clients.ID", ondelete="CASCADE"), nullable=False)
    FromClient: Mapped[bytes]= mapped_column(BLOB, ForeignKey("clients.ID", ondelete="CASCADE"), nullable=False)
    Type: Mapped[int]        = mapped_column(Integer, nullable=False)
    Content: Mapped[bytes]   = mapped_column(BLOB, nullable=False)

    __table_args__ = (
        CheckConstraint("length(ToClient)=16", name="ck_msg_to_16"),
        CheckConstraint("length(FromClient)=16", name="ck_msg_from_16"),
        CheckConstraint("Type BETWEEN 0 AND 255", name="ck_msg_type_byte"),
        CheckConstraint("ID BETWEEN 0 AND 4294967295", name="ck_msg_id_u32"),
    )
