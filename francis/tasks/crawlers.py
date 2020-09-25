from discord.ext import tasks, commands

from .genshin import GenshinCrawler
from .gms import GMSCrawler
from .honkai import HonkaiWikiCrawler, HonkaiWebCrawler


class WebCralers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('Initializing [Genshin Crawler: Web API]')
        self.genshin_crawler = GenshinCrawler(bot)
        print('Initializing [Honkai Crawler: Web | Wiki]')
        self.honkai_wiki_crawler = HonkaiWikiCrawler(bot)
        self.honkai_web_crawler = HonkaiWebCrawler(bot)
        print('Initializing [GMS Crawler: Web]')
        self.gms_crawler = GMSCrawler(bot)
        self.do_crawl.start()

    def cog_unload(self):
        self.do_crawl.cancel()

    @tasks.loop(seconds=60.0)
    async def do_crawl(self):
        await self.genshin_crawler.do_crawl()
        await self.honkai_wiki_crawler.do_crawl()
        await self.honkai_web_crawler.do_crawl()
        await self.gms_crawler.do_crawl()

    @do_crawl.before_loop
    async def before_parse(self):
        print('[Web Crawlers] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[Web Crawlers] Ready and running!')


def setup(bot):
    bot.add_cog(WebCralers(bot))
