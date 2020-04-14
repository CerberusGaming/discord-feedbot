import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

from DiscordFeedBot.Common.storage import Base


class FeedModel(Base):
    __tablename__ = "feeds"
    feed_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True, comment="Feed ID/PK.")
    feed_enabled = Column(Boolean, nullable=False, default=True, comment="Feed pause status.")

    feed_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())

    guild = Column(BigInteger, nullable=False, comment="Discord Guild ID.")
    channel = Column(BigInteger, nullable=False, comment="Discord Channel ID.")

    feed_type = Column(String(32), nullable=False, comment="Type of feed handler.")
    feed_param = Column(String(8000), comment="Additional handler parameter (Optional).")
    feed_extra = Column(String(8000), comment="Extra params for the handler (Optional).")
