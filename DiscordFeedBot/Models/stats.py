import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer

from DiscordFeedBot.Common.storage import Base


class StatsModel(Base):
    __tablename__ = "stats"
    stats_id = Column(BigInteger, nullable=True, primary_key=True, autoincrement=True)

    guilds = Column(Integer, nullable=False, default=0)
    channels = Column(Integer, nullable=False, default=0)
    feeds = Column(Integer, nullable=False, default=0)
    entries = Column(Integer, nullable=False, default=0)
    posts = Column(Integer, nullable=False, default=0)

    stats_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow().replace(microsecond=0))
