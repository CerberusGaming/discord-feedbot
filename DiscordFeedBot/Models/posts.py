import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer

from DiscordFeedBot.Common.storage import Base


class PostModel(Base):
    __tablename__ = "posts"
    post_id = Column(BigInteger, nullable=True, primary_key=True, autoincrement=True)

    feed_id = Column(Integer, nullable=False)
    entry_id = Column(Integer, nullable=False)

    post_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow().replace(microsecond=0))
