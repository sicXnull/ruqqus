import time
from sqlalchemy import *
from sqlalchemy.orm import relationship

from ruqqus.helpers.base36 import *
from ruqqus.__main__ import Base, db


class MODs(Base):
    __tablename__ = "mods"
    id = Column(BigInteger, primary_key=True)
    uid = Column(Integer, ForeignKey("users.id"))
    board_id = Column(BigInteger, ForeignKey("submissions.board_id"))
    is_banned = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        if "created_utc" not in kwargs:
            kwargs["created_utc"] = int(time.time())

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Boards(id={self.id}, uid={self.uid}, board_id={self.board_id})>"