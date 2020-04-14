from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import Config

_config = Config()
_engine_url = _config.get("storage", 'uri')
_engine_config = dict()
if not _engine_url.startswith("sqlite"):
    _engine_config.update(pool_size=_config.get('storage', 'pool', default=5, wrap=int))
    _engine_config.update(max_overflow=_config.get('storage', 'overflow', default=10, wrap=int))
_engine = create_engine(_engine_url, **_engine_config)

Base = declarative_base(bind=_engine)


def Session(bind=_engine):
    return scoped_session(sessionmaker(bind=bind))()
