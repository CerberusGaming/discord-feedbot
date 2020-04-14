import glob
import hashlib
import importlib
import inspect
import os

from discord import Embed


class FeedEmbed(Embed):
    pass


class FeedEntry:
    def __init__(self, data: dict):
        self.data = data
        self.uid = self._generate_data_hash(data)

    @staticmethod
    def _generate_data_hash(data):
        data = ''.join(["'%s':'%s';" % (key, val) for (key, val) in sorted(data.items())])
        return hashlib.sha1(data.encode("utf-8")).hexdigest()


class BaseFeed:
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
        return FeedEmbed()


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
                    c: BaseFeed = item[1]
                    self.feeds.update({c.feed_type.lower(): c.feed_type})
                    setattr(self, c.feed_type, c)

    def _predicate(self, entry):
        if inspect.isclass(entry) and not inspect.isabstract(entry):
            return BaseFeed in entry.__bases__
        else:
            return False
