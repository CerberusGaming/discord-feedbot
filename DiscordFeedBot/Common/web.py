import datetime
import os
from uuid import uuid4

from flask import Flask
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func, Date

from DiscordFeedBot.Common.storage import Session
from DiscordFeedBot.Models.stats import StatsModel


class IndexView(AdminIndexView):
    @expose("/")
    def index(self):
        data = {}
        ses = Session()

        stats_now: StatsModel = ses.query(StatsModel).order_by(StatsModel.stats_date.desc()).first()
        if stats_now is not None:
            data.update({
                "total_feeds": stats_now.feeds,
                "channels": stats_now.channels,
                "guilds": stats_now.guilds
            })

        now = datetime.datetime.utcnow().replace(microsecond=0, second=0, minute=0, hour=0).date()
        dates = [(now - datetime.timedelta(days=x)) for x in range(0, 29, 1)]

        feeds_hist = []
        entries_hist = []
        posts_hist = []
        for entry in dates:
            entry = ses.query(func.avg(StatsModel.feeds), func.avg(StatsModel.entries),
                              func.avg(StatsModel.posts)).filter(StatsModel.stats_date.cast(Date) == entry).first()
            feeds, entries, posts = entry
            feeds_hist.append(round(feeds, 0) if feeds is not None else 0)
            entries_hist.append(round(entries, 0) if entries is not None else 0)
            posts_hist.append(round(posts, 0) if posts is not None else 0)
        data.update({"feeds_hist": [str(x) for x in feeds_hist],
                     "entries_hist": [str(x) for x in entries_hist],
                     "posts_hist": [str(x) for x in posts_hist],
                     "hist_dates": [x.strftime("%Y-%m-%d") for x in dates]})
        ses.close()
        return self.render("index.html", data=data)


class WebPanel(Flask):
    def __init__(self, debug: bool = False):
        super(WebPanel, self).__init__(__name__)
        self.debug = debug

        self.template_folder = os.path.normpath(os.getcwd() + "/templates")
        self.secret_key = str(uuid4())
        self.admin = Admin(self, name="FeedBot Admin", index_view=IndexView(url="/"), template_mode='bootstrap3')

    def add_model(self, models: list):
        for model in models:
            self.admin.add_views(ModelView(model, Session()))
