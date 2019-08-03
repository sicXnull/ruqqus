import time
from sqlalchemy import *
from sqlalchemy.orm import relationship

from ruqqus.helpers.base36 import *
from ruqqus.__main__ import Base, db


class Boards(Base):
    __tablename__ = "boards"
    id = Column(BigInteger, primary_key=True)
    board_name = Column(String, default=None)
    board_id = Column(BigInteger, ForeignKey("submissions.board_id"))
    is_banned = Column(Boolean, default=False)
    created_utc = Column(Integer, default=None)
    mods = relationship('MODs', lazy="dynamic", backref="users")

    def __init__(self, *args, **kwargs):
        if "created_utc" not in kwargs:
            kwargs["created_utc"] = int(time.time())

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Boards(id={self.id}, board_id={self.board_id}, mods={self.mods})>"