import time
from sqlalchemy import *
from sqlalchemy.orm import relationship

from ruqqus.helpers.base36 import *
from ruqqus.__main__ import Base, db


class DMs(Base):
    __tablename__ = "dms"
    id = Column(BigInteger, primary_key=True)
    to_user_id = Column(Integer, ForeignKey("users.id"))
    from_user_id = Column(Integer, ForeignKey("users.id"))
    parent_dm_id = Column(BigInteger, default=None)
    body = Column(String(5000), default=None)
    body_html = Column(String)
    created_utc = Column(Integer, default=None)
    is_banned = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        if "created_utc" not in kwargs:
            kwargs["created_utc"] = int(time.time())

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<DMs(id={self.id}, uid={self.user_id}, from_uid={self.from_user_id}," \
               f" to_uid={self.to_user_id}, parent_dm_id={self.parent_dm_id}, created={self.created_utc})>"
