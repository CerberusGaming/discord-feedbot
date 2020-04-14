from uuid import uuid4

from flask import Flask, redirect
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from DiscordFeedBot.Common.storage import Session


class WebPanel(Flask):
    def __init__(self):
        super(WebPanel, self).__init__(__name__)
        self.secret_key = str(uuid4())
        self.admin = Admin(self, name="FeedBot Admin")

        @self.route("/")
        def index():
            return redirect("/admin")

    def add_model(self, model):
        self.admin.add_views(ModelView(model, Session()))
