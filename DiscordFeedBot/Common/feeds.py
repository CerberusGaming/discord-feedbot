import glob
import hashlib
import importlib
import inspect
import os

from discord import Embed


class FeedEmbed(Embed):
    uuid: str = None
    hidden: bool = None
    nsfw: bool = None

    def __init__(self, **kwargs):
        super(FeedEmbed, self).__init__(**kwargs)
        self.hidden = str(kwargs.get("hidden", "false")).lower() == "true"
        self.nsfw = str(kwargs.get("nsfw", "false")).lower() == "true"
        self.uuid = str(kwargs.get("uuid", self._generate_data_hash(self.to_dict())))

    @staticmethod
    def _generate_data_hash(data):
        data = ''.join(["'%s':'%s';" % (key, val) for (key, val) in sorted(data.items())])
        return hashlib.sha1(data.encode("utf-8")).hexdigest()

    def to_dict(self):
        data = super(FeedEmbed, self).to_dict()
        data.update({'uuid': self.uuid, 'hidden': self.hidden, 'nsfw': self.nsfw})
        return data

    def from_dict(self, data):
        retr = super(FeedEmbed, self).from_dict(data)
        retr.hidden = data.get('hidden')
        retr.nsfw = data.get('nsfw')
        retr.uuid = data.get('uuid')
        return retr


class FeedBase:
    feed_type: str = ""
    feed_param: str = ""

    feed_help: str = ""

    refresh: int = 60
    limit: int = 100

    def __init__(self, param: str = None, **kwargs):
        self.param = param

    def get_entries(self):
        return []

    def create_embed(self, post: dict):
        return FeedEmbed(**post)


class FeedManager:
    def __init__(self):
        self.feeds = {}
        self.refresh()

    def refresh(self):
        path = os.path.normpath("./DiscordFeedBot/Feeds/*")
        for file in glob.glob(path):
            if not os.path.basename(file).startswith("__"):
                package = file.replace(".py", "").replace("\\", ".").replace("/", ".")
                package = importlib.import_module(package)
                for item in inspect.getmembers(package, self._predicate):
                    c: FeedBase = item[1]
                    self.feeds.update({c.feed_type.lower(): c.feed_type})
                    setattr(self, c.feed_type, c)

    def _predicate(self, entry):
        if inspect.isclass(entry) and not inspect.isabstract(entry):
            return FeedBase in entry.__bases__
        else:
            return False
