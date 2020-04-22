import datetime

from requests import Session

from DiscordFeedBot.Common.feeds import FeedBase, FeedEmbed


class RedditFeedEmbed(FeedEmbed):
    def __init__(self, post: dict):
        data = {"uuid": post.get('id'),
                "url": "https://www.reddit.com" + post.get('permalink', ""),
                "timestamp": datetime.datetime.fromtimestamp(post.get('created_utc', 0)),
                "nsfw": post.get('over_18')
                }
        if any([post.get('hidden'), post.get('stickied'), post.get('quarantine')]):
            data.update({"hidden": True})
        super(RedditFeedEmbed, self).__init__(**data)
        self.set_author(name=post.get('author'))

        title = post.get('title')
        description = "Link: " + post.get('url', "")
        if len(title) > 99:
            description = title + "\n" + description
            title = title[0:97] + "..."
        self.title = title
        self.description = description

        if post.get("thumbnail", None) is not None:
            try:
                image: str = post.get("media").get("oembed").get("thumbnail_url")
                assert image.lower().startswith("https")
                self.set_image(url=image)
            except:
                image: str = post.get("thumbnail")
                if image.startswith("https"):
                    self.set_image(url=image)


class RedditFeed(FeedBase):
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

    def get_entries(self, limit: int = 100):
        req = self._session.get(self._url + "&limit={}".format(str(limit)))
        if req.status_code == 200:
            posts = [RedditFeedEmbed(x['data']) for x in req.json()['data']['children']]
        else:
            posts = []
        return posts

    def create_embed(self, post: dict):
        return RedditFeedEmbed({}).from_dict(post)
