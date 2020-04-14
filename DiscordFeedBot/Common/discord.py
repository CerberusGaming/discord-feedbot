import inspect

from discord import Client, Message

from .config import Config
from .feeds import FeedManager
from .storage import Base
from .web import WebPanel


class Discord(Client):
    def __init__(self, *, loop=None, **options):
        super(Discord, self).__init__(loop=loop, **options)
        Base.metadata.create_all()

        self.config = Config()
        self.prefix = self.config.get('discord', 'prefix', default="!")

        self.feeds = FeedManager()
        self.web = WebPanel()

    def run_discord(self, **kwargs):
        return super(Discord, self).run(self.config.get('discord', 'token'), **kwargs)

    def run_webserver(self):
        return self.web.run(self.config.get('web', 'host', default="0.0.0.0"),
                            self.config.get('web', 'port', default="7777", wrap=int))

    def command_parser(self, content: str):
        content = " ".join([x.lstrip().rstrip() for x in content.split(" ") if len(x.replace(" ", "")) > 0])
        content = " ".join([x.lstrip().rstrip() for x in content.replace(" =", "=").replace("= ", "=").split(" ")])
        content = content.split(" ", 1)
        if len(content) == 2:
            command, content = content
        else:
            command = content[0]
            content = ""

        args = []
        kwargs = {}
        while len(content) > 0:
            item = content.split(" ", 1)
            if len([x for x in item if len(x.lstrip().rstrip()) > 0]) > 1:
                item, content = item
            else:
                item = item[0]
                content = ''

            kwarg = None
            starts = None
            if item.startswith("'"):
                starts = "'"
            elif item.startswith('"'):
                starts = '"'
            elif item.startswith("?"):
                item = item.split("=")
                kwarg, item = item
                if item.startswith("'"):
                    starts = "'"
                elif item.startswith('"'):
                    starts = '"'
            if starts is not None:
                while True:
                    if item.endswith(starts) or len(content) == 0:
                        break
                    adtl = content.split(" ", 1)
                    if len([x for x in adtl if len(x.lstrip().rstrip()) > 0]) > 1:
                        adtl, content = adtl
                    else:
                        adtl = adtl[0]
                        content = ''
                    item = item + " " + adtl

                item = item.rstrip(starts).lstrip(starts)

            if kwarg is not None:
                kwargs.update({str(kwarg).lstrip("?"): item})
            else:
                args.append(item)

        return command.lstrip(self.prefix), args, kwargs

    async def on_message(self, message: Message):
        if message.content.lower().startswith(self.prefix):
            command, args, kwargs = self.command_parser(message.content)
            command = "command_" + command.lstrip(self.prefix).lower()
            if hasattr(self, command):
                command = getattr(self, command)
                await command(message=message, args=args, kwargs=kwargs)

    @staticmethod
    def _task_predicate(value):
        if inspect.iscoroutinefunction(value):
            if str(value.__name__).startswith("task_"):
                return True
        return False

    def _task_loader(self):
        for item in inspect.getmembers(self, predicate=self._task_predicate):
            try:
                name, method = item
                self.loop.create_task(method())
            except:
                pass

    async def on_ready(self):
        print("Bot Online")
        self._task_loader()
        pass
