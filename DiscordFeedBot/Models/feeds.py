import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

from DiscordFeedBot.Common.storage import Base


class FeedModel(Base):
    __tablename__ = "feeds"
    feed_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    feed_enabled = Column(Boolean, nullable=False, default=True)
    feed_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow().replace(microsecond=0))

    guild = Column(BigInteger, nullable=False)
    channel = Column(BigInteger, nullable=False)

    feed_type = Column(String(32), nullable=False)
    feed_param = Column(String(8000))
    feed_extra = Column(String(8000))
