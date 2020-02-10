import json
import re
from datetime import datetime

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks, commands

from web.apps.pricewatchers.models import TikiProduct
from .webspiders import WebSpider


class HonkaiTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reg = re.compile('\s*var\s*defaultProduct\s*=\s*({.*})')
        self.fetch_tiki_products_price.start()
        self.site = 'https://tiki.vn'
        self.promo_endpoint = 'https://tiki.vn/api/promon/v1/products/sale-attrs'
        # self.tiki_channel_id = 676382684699820063

    @commands.command(name='tikiadd', hidden=True)
    @commands.is_owner()
    async def _add_tiki_page(self, context, page_id):
        tiki_product_obj, created = TikiProduct.objects.get_or_create(page_id=page_id)
        if created:
            message = 'Successfully added Tiki product to check for price.'
        else:
            message = 'This page ID has already been added.'
        await context.say_as_embed(message)

    @commands.command(name='tikidel', hidden=True)
    @commands.is_owner()
    async def _delete_tiki_page(self, context, page_id):
        tiki_product_obj = TikiProduct.objects.filter(page_id=page_id).first()
        if tiki_product_obj:
            tiki_product_obj.delete()
            message = 'Successfully deleted Tiki product.'
        else:
            message = 'This page ID does not exist.'

        await context.say_as_embed(message)

    @tasks.loop(seconds=60)
    async def fetch_tiki_products_price(self):

        channel = self.bot.get_channel(676382684699820063)
        if not channel:
            return

        tiki_product_objs = TikiProduct.objects.all()
        for product_obj in tiki_product_objs:
            # that extra '-' is for discord quick link to tiki app to work
            url = f'{self.site}/-{product_obj.page_id}.html'
            html = WebSpider.get_content_by_url(url)
            if not html:
                continue

            bs = BeautifulSoup(html, 'html.parser')

            image_url = bs.select_one('#product-magiczoom')
            image_url = image_url.get('data-zoom-image', None) if image_url else None

            product_name = bs.select_one('.item-name')
            product_name = product_name.get_text().strip() if product_name else product_obj.page_id

            scripts = bs.find_all('script')
            data = self.parse_product_data(scripts)

            embed = discord.Embed(
                title=product_name,
                url=f'{url}',
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text='tiki.vn', icon_url='https://tiki.vn/favicon-32x32.png')
            if image_url:
                embed.set_thumbnail(url=image_url)

            if not data:
                continue
            elif 'out_of_stock' in data:
                if product_obj.out_of_stock is False:
                    embed.description = (
                        f'• Trạng thái: **Hết hàng**\n'
                    )
                    await channel.send(embed=embed)

                    product_obj.out_of_stock = True
                    product_obj.save()
                continue

            all_sellers = [data['current_seller']]
            if 'other_sellers' in data:
                all_sellers += data['other_sellers']

            # sorted by price ascending
            for seller in all_sellers:
                product_id = seller.get('product_id', None)
                product_price = seller.get('price', None)
                if not product_id or not product_price:
                    continue
                promo_payload = f'[{{"id":"{product_id}","price":{product_price}}}]'
                promo_response = requests.post(self.promo_endpoint, data=promo_payload)
                if promo_response.status_code != 200:
                    continue
                promo_code_list = promo_response.json()['data'][product_id]
                price_list = [code['price'] for code in promo_code_list]
                if not price_list:
                    continue
                lowest_price = min(price_list)
                seller['price'] = lowest_price

            seller_sorted = sorted(all_sellers, key=lambda abc: abc['price'])

            if not seller_sorted:
                continue

            best_seller = seller_sorted[0]
            best_price = best_seller['price']
            seller_name = best_seller['name']

            product_obj.out_of_stock = False

            if product_obj.current_lowest_price == best_price:
                product_obj.save()
                continue

            lowest_price = best_price if best_price < product_obj.lowest_price else product_obj.lowest_price

            embed.description = (
                f'```bash\n'
                f'GIÁ\n'
                f'• Cũ        : {product_obj.current_lowest_price:>13,}\n'
                f'• Mới       : {best_price:>13,}\n'
                f'• Thấp nhất : {lowest_price:>13,}\n'
                f'---\n'
                f'NHÀ BÁN HÀNG\n'
                f'• Tên : {seller_name}\n'
                f'```'
            )
            await channel.send(embed=embed)

            product_obj.current_lowest_price = best_price
            product_obj.product_name = product_name

            if product_obj.lowest_price > best_price:
                product_obj.lowest_price = best_price
            product_obj.save()

    def parse_product_data(self, script_tags):
        for script in script_tags:
            text = script.get_text()
            reg_result = self.reg.search(text)
            if reg_result:
                try:
                    json_data = json.loads(reg_result.group(1))
                    return json_data
                except json.JSONDecodeError:
                    pass
            elif 'defaultProduct = null' in text:
                return {'out_of_stock': {'status': True}}
        return None

    @fetch_tiki_products_price.before_loop
    async def before_parse(self):
        print('[Tiki Product price watcher] Waiting for ready state...')

        await self.bot.wait_until_ready()

        print('[Tiki Product price watcher] Ready and running!')

    def cog_unload(self):
        self.fetch_tiki_products_price.cancel()


def setup(bot):
    bot.add_cog(HonkaiTasks(bot))
