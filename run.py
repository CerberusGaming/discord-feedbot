from threading import Thread

from DiscordFeedBot.bot import DiscordBot

if __name__ == "__main__":
    threads = []
    bot = DiscordBot()
    if bot.config.get("web", "enabled", default="false", wrap=bool):
        threads.append(Thread(target=bot.run_webserver, daemon=True))
    threads.append(Thread(target=bot.run_discord, daemon=False))

    for thread in threads:
        thread.start()
