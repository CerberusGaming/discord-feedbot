import os
from uuid import uuid4

from flask import Flask
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from DiscordFeedBot.Common.storage import Session


class IndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render("index.html")


class WebPanel(Flask):
    def __init__(self, debug: bool = False):
        super(WebPanel, self).__init__(__name__)
        self.debug = debug

        self.template_folder = os.path.normpath(os.getcwd() + "/templates")
        self.secret_key = str(uuid4())
        self.admin = Admin(self, name="FeedBot Admin", index_view=IndexView(url="/"))
        self.admin.template_mode = 'bootstrap3'

    def add_model(self, models: list):
        for model in models:
            self.admin.add_views(ModelView(model, Session()))
