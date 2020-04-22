import datetime
import html

from requests import Session

from DiscordFeedBot.Common.feeds import BaseFeed, FeedEntry, FeedEmbed


class RedditFeedEmbed(FeedEmbed):
    def __init__(self, post: dict):
        super(FeedEmbed, self).__init__()
        self.description = ""

        self.title = html.unescape(post['title'])
        if len(self.title) > 100:
            self.description = self.title
            self.title = self.title[0:100] + "..."

        if len(self.description) > 0:
            self.description = self.description + "\n"

        if len(post.get('url', "")) > 0:
            self.description = self.description + "Link: " + post['url']

        self.set_author(name=post['author'])
        self.timestamp = datetime.datetime.fromtimestamp(int(post['created_utc']))
        self.url = "https://reddit.com{}".format(post['permalink'])

        if str(post['thumbnail']).startswith("https"):
            self.set_image(url=post['thumbnail'])

        self.id = post['id']
        self.nsfw = post['over_18']
        self.hidden = post['stickied']


class RedditFeedEntry(FeedEntry):
    def __init__(self, data: dict):
        super(RedditFeedEntry, self).__init__(data)
        self.data = data
        self.uid = data['id']


class RedditFeed(BaseFeed):
    feed_type = "Reddit"
    feed_help = "Gets feeds from reddit.com.\n" \
                "{p}feed add {n} <subreddit>"

    def __init__(self, param, **kwargs):
        super(RedditFeed, self).__init__(param, **kwargs)
        self.param = "r/{}".format(self.param.lower().split('/')[-1])
        self._url = "https://www.reddit.com/{}.json?sort=new".format(self.param)
        self._session = Session()
        self._session.headers.update({'Accept': 'application/json',
                                      "User-Agent": "server:discord.hook.bot:v0 (by /u/DACRepair)"})

        self.ignore_nsfw = kwargs.get("ignore_nsfw", "false").lower() == "true"
        self.ignore_hidden = kwargs.get("ignore_hidden", "false").lower() == "true"

    def get_entries(self, limit: int = 100):
        req = self._session.get(self._url + "&limit={}".format(str(limit)))
        if req.status_code == 200:
            posts = [RedditFeedEntry(x['data']) for x in req.json()['data']['children']]
        else:
            posts = []
        return posts

    def create_embed(self, post: dict, nsfw: bool):
        embed = RedditFeedEmbed(post)
        if self.ignore_nsfw:
            nsfw = True
        else:
            nsfw = all([nsfw, embed.nsfw])

        if self.ignore_hidden:
            hidden = True
        else:
            hidden = not embed.hidden
        if hidden and nsfw:
            return embed
        return None
