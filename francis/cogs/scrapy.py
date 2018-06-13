# import asyncio
# import json
# import os
# import scrapy

# from discord.ext import commands
# import discord

# from scrapy.crawler import CrawlerProcess


# class GmssitebotSpider(scrapy.Spider):
#     name = 'gmssitebot'
#     allowed_domains = ['maplestory.nexon.net/news']
#     start_urls = ['http://maplestory.nexon.net/news/']

#     # cogs/scrapy.py -> cogs
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#     def parse(self, response):
#         titles = response.css('.news-container .news-item .text h3 a::text').extract()
#         urls = response.css('.news-container .news-item .text h3 a::attr(href)').extract()
#         photos = response.css('.news-container .news-item .photo::attr(style)').extract()

#         proc_photos = list()
#         for p in photos:
#             proc = p.lstrip('background-image:url(').rstrip(')')
#             proc_photos.append(proc)

#         yield_data = list()
#         for item in zip(titles, urls, proc_photos):
#             data = {
#                 'title': item[0],
#                 'url': item[1],
#                 'photo': item[2]
#             }

#             yield_data.append(data)

#         print('**** YIELD DATA *****', yield_data)
#         with open(self.BASE_DIR + '/scraper/gmssite.json', 'r') as infile:
#             file_data = json.load(infile)
#             # pass if no new data found
#             if file_data == yield_data:
#                 print('*** NO NEW DATA COLLECTED ***')
#             # rewrite the file with new data
#             else:
#                 yield yield_data
#                 with open(self.BASE_DIR + '/gmssite.json', 'w') as outfile:
#                     json.dump(yield_data, outfile)


# class Scraper:
#     """A cog for Scraping stuff"""

#     def __init__(self, bot, util):
#         self.bot = bot
#         self.util = util

#     async def start_spider(self):
#         await self.bot.wait_until_ready()

#         while not self.bot.is_closed:
#             process = CrawlerProcess({
#                 'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
#             })
#             p = process.crawl(GmssitebotSpider)
#             print(dir(p))
#             await asyncio.sleep(20)
#         process.start()
