import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from DiscordFeedBot.Common.storage import Base


class EntryModel(Base):
    __tablename__ = "entries"
    entry_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    feed_type = Column(String(32), nullable=False)
    feed_param = Column(String(8000), nullable=False)

    entry_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow().replace(microsecond=0))

    entry_uid = Column(String(255), nullable=False, unique=True)
    entry_data = Column(Text, nullable=False, default="")
