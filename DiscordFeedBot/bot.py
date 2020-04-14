import asyncio
import json

from discord import Message, Guild, TextChannel

from DiscordFeedBot.Common.discord import Discord
from DiscordFeedBot.Common.feeds import BaseFeed, FeedEntry
from DiscordFeedBot.Common.storage import Session
from DiscordFeedBot.Models.entries import EntryModel
from DiscordFeedBot.Models.feeds import FeedModel
from DiscordFeedBot.Models.posts import PostModel


class DiscordBot(Discord):
    def __init__(self):
        super(DiscordBot, self).__init__()
        self.web.add_model(FeedModel)

    async def task_entry_manager(self):
        processors = {}
        while self.loop.is_running():
            for feed_id, future in processors.copy().items():
                if future.done():
                    del processors[feed_id]

            ses = Session()
            feeds = ses.query(FeedModel.feed_type, FeedModel.feed_param)
            for feed in feeds.filter(FeedModel.feed_enabled).group_by(FeedModel.feed_type, FeedModel.feed_param).all():
                feed_type, feed_param = feed
                proc_name = "{}_{}".format(feed_type, feed_param)
                if proc_name not in processors.keys():
                    processors[proc_name] = self.loop.create_task(self.entry_processor(feed_type, feed_param))
            ses.close()

            await asyncio.sleep(10)

    async def task_post_manager(self):
        processors = {}
        while self.loop.is_running():
            for feed_id, future in processors.copy().items():
                if future.done():
                    del processors[feed_id]

            ses = Session()
            for feed in ses.query(FeedModel.feed_id).filter(FeedModel.feed_enabled).all():
                feed_id = feed[0]
                if feed_id not in processors.keys():
                    processors[feed_id] = self.loop.create_task(self.post_processor(feed_id))
            ses.close()

            await asyncio.sleep(10)

    async def command_feed(self, message: Message, args: list = None, kwargs: dict = None):
        # Channel Managers Only
        # !feed <list, add, del, pause> <type> <params>
        if message.guild is not None:
            server_admin = message.author.guild_permissions.administrator
            channel_admin = message.author.permissions_in(message.channel).manage_channels
            permitted = any([server_admin, channel_admin])
        else:
            permitted = False

        help_text = "The available bot commands are:```\n" \
                    "{prefix}feed [h, help]: What you see now. you can also do {prefix}help <command>\n" \
                    "\n" \
                    "commands:\n" \
                    "{prefix}feed list: Lists all feeds\n" \
                    "{prefix}feed add: Adds a feed\n" \
                    "{prefix}feed delete: Deletes a feed\n" \
                    "{prefix}feed pause: Pauses a feed (stops posting in discord)```".format(prefix=self.prefix)

        if permitted:
            ses = Session()
            if len(args) == 0:
                await message.channel.send(help_text)
            elif args[0].lower() in ('h', 'help'):
                if len(args) > 1:
                    if args[1] in ('h', 'help'):
                        await message.channel.send("My brain hurts...")
                    elif args[1] in ('l', 'ls', 'list'):
                        await message.channel.send("```"
                                                   "{p}feed list\n"
                                                   "Lists all feeds in this channel."
                                                   "```".format(p=self.prefix))
                    elif args[1] in ('a', 'add'):
                        if len(args) > 2 and str(args[2]).lower() in self.feeds.feeds.keys():
                            feed_name = self.feeds.feeds[args[2]]
                            handlers = getattr(self.feeds, feed_name).feed_help.format(p=self.prefix, n=feed_name)
                            handlers = "{n} Handler:\n" \
                                       "{h}".format(n=feed_name, h=handlers)
                        else:
                            handlers = "Available Handlers:\n" \
                                       "{h}".format(h=", ".join(self.feeds.feeds.values()))
                        await message.channel.send("```"
                                                   "{p}feed add <handler> [handler args]\n"
                                                   "Adds a feed to the current channel\n"
                                                   "\n"
                                                   " - handler: What type of feed.\n"
                                                   " - handler args: Arguments for the handler.\n"
                                                   "   Use: {p}feed help add <handler> to see them.\n"
                                                   "\n"
                                                   "{h}"
                                                   "```".format(p=self.prefix, h=handlers))
                    elif args[1] in ('d', 'del', 'delete'):
                        await message.channel.send("```"
                                                   "{p}feed delete <feed id>\n"
                                                   "Deletes a feed in the current channel.\n"
                                                   "\n"
                                                   " - feed id:(see +feed list)\n"
                                                   "\n"
                                                   "NOTE: There is no warning and\n"
                                                   "this is permanent!"
                                                   "```".format(p=self.prefix))
                    elif args[1] in ('p', 'pause'):
                        await message.channel.send("```{p}feed pause <feed id> [clean]\n"
                                                   "Pauses / Unpauses a feed in the current channel.\n"
                                                   "\n"
                                                   " - feed id: (see {p}feed list)\n"
                                                   " - clean: if you don't want to pick up where you left off,\n"
                                                   "   you can add a \"clean\" to the end of the command to delete\n"
                                                   "   the messages posted while paused.\n"
                                                   "```".format(p=self.prefix))
                else:
                    await message.channel.send(help_text)

            elif args[0].lower() in ('l', 'ls', 'list'):
                msg = []
                feeds = ses.query(FeedModel).filter(FeedModel.channel == message.channel.id,
                                                    FeedModel.guild == message.guild.id)
                for item in feeds.all():
                    item: FeedModel

                    fid = str(item.feed_id)
                    fid = (" " * (11 - len(fid))) + fid[0:min(len(fid), 11)]
                    ftype = str(item.feed_type)
                    ftype = ftype[0:min(len(ftype), 9)] + ("~" if len(ftype) > 9 else "") + (" " * (10 - len(ftype)))
                    fparam = str(item.feed_param)
                    fparam = fparam + (" " * max((10 - len(fparam)), 0))
                    fpause = " [PAUSED]" if not item.feed_enabled else ""

                    msg.append("{} | {} | {} {}".format(fid, ftype, fparam, fpause))

                await message.channel.send("```Current feeds for {channel}:\n"
                                           "Feed ID     | Type       | Parameters\n"
                                           "----------- | ---------- | ----------\n"
                                           "{feeds}```".format(channel=message.channel.name, feeds="\n".join(msg)))

            elif args[0].lower() in ('a', 'add'):
                if len(args) < 2:
                    await message.channel.send("Invalid, try `{p}feed help add`".format(p=self.prefix))
                else:
                    if len(args) > 2:
                        handler: BaseFeed = getattr(self.feeds, str(args[1]).title(), None)
                        if handler is not None:
                            hname = str(handler.feed_type)
                            param = str(" ".join(args[2:]))

                            kwargs = json.dumps(kwargs)

                            ses.add(FeedModel(
                                guild=message.guild.id,
                                channel=message.channel.id,
                                feed_type=hname,
                                feed_param=param,
                                feed_extra=kwargs
                            ))
                            ses.commit()
                            await message.channel.send("Added {} Feed: {}".format(hname, param))
                        else:
                            await message.channel.send("Invalid, try `{p}feed help add`".format(p=self.prefix))

            elif args[0].lower() in ('d', 'del', 'delete'):
                if len(args) > 1:
                    feed_id = int(args[1])
                    feedx = ses.query(FeedModel).filter(FeedModel.feed_id == feed_id).filter(
                        FeedModel.channel == message.channel.id, FeedModel.guild == message.guild.id)
                    if feedx.count() > 1 or feedx.count() == 0:
                        await message.channel.send("Invalid feed id: {}".format(feed_id))
                    else:
                        ses.delete(feedx.one())
                        ses.commit()
                        # CLEAN UP HERE?
                        await message.channel.send("Successfully deleted feed id: {}".format(feed_id))
                else:
                    await message.channel.send("Invalid, try `{p}feed help delete`".format(p=self.prefix))

            elif args[0].lower() in ('p', 'pause'):
                if len(args) > 1:
                    feed_id = int(args[1])
                    clean = False
                    if len(args) > 2:
                        if str(args[2]).lower() == "clean":
                            clean = True
                    feeds = ses.query(FeedModel).filter(FeedModel.feed_id == feed_id)
                    feeds = feeds.filter(FeedModel.channel == message.channel.id, FeedModel.guild == message.guild.id)
                    if feeds.count() > 1 or feeds.count == 0:
                        await message.channel.send("Invalid feed id: {}".format(feed_id))
                    else:
                        feed: FeedModel = feeds.first()
                        enabled = feed.feed_enabled
                        if enabled:
                            feed.feed_enabled = False
                            ses.commit()
                            await message.channel.send("Paused feed id: {}".format(feed_id))
                        else:
                            clean_msg = ""
                            if clean:
                                pass
                            feed.feed_enabled = True
                            ses.commit()
                            await message.channel.send("Unpaused feed id: {}{}".format(feed_id, clean_msg))

            else:
                await message.channel.send(help_text)
            ses.close()

        else:
            await message.channel.send("You do not have permission for that")

    async def entry_processor(self, feed_type: str, feed_param: str):
        while self.loop.is_running():
            handler: BaseFeed = getattr(self.feeds, self.feeds.feeds[feed_type.lower()])(param=feed_param)
            ses = Session()
            for entry in handler.get_entries():
                entry: FeedEntry
                if ses.query(EntryModel).filter(EntryModel.feed_type == feed_type, EntryModel.feed_param == feed_param,
                                                EntryModel.entry_uid == entry.uid).count() == 0:
                    ses.add(EntryModel(feed_type=feed_type,
                                       feed_param=feed_param,
                                       entry_uid=entry.uid,
                                       entry_data=json.dumps(entry.data)))
                    ses.commit()
            ses.close()
            await asyncio.sleep(handler.refresh)

    async def post_processor(self, feed_id: int):
        while self.loop.is_running():
            ses = Session()
            feed: FeedModel = ses.query(FeedModel).filter(FeedModel.feed_id == feed_id).first()
            if feed is None:
                break
            extra = json.loads(feed.feed_extra)
            handler: BaseFeed = getattr(self.feeds, self.feeds.feeds[feed.feed_type.lower()])(feed.feed_param, **extra)

            entries = ses.query(EntryModel) \
                .filter(EntryModel.feed_type == feed.feed_type, EntryModel.feed_param == feed.feed_param) \
                .filter(EntryModel.entry_created >= feed.feed_created) \
                .outerjoin(PostModel, PostModel.entry_id == EntryModel.entry_id) \
                .filter(PostModel.feed_id == None) \
                .order_by(EntryModel.entry_created.asc())

            for entry in entries.all():
                entry: EntryModel
                embed = handler.create_embed(json.loads(entry.entry_data))
                if embed is not None:
                    embed.set_footer(text="Discord Feedbot: {} - {}".format(feed.feed_type, feed.feed_param))
                    guild: Guild = self.get_guild(feed.guild)
                    channel: TextChannel = guild.get_channel(feed.channel)
                    try:
                        if await channel.send(embed=embed) is not None:
                            ses.add(PostModel(feed_id=feed.feed_id, entry_id=entry.entry_id))
                            ses.commit()
                    except:
                        print(embed.to_dict())
            await asyncio.sleep(10)
