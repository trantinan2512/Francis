from utils import time
from gspread.exceptions import APIError
import asyncio
import re
from datetime import datetime


async def match_word_event(message, channel, bot, event_db, valid_words, sleep=5):

    try:
        latest_row = event_db.row_values(2)
        if latest_row:
            latest_uid, latest_word, latest_ts = latest_row[0], latest_row[2], latest_row[3]
        else:
            latest_uid, latest_word, latest_ts = None, None, None
    except APIError:
        failed_note = await bot.send_message(
            channel,
            f'Em mệt quá, cho em nghỉ xíu nha :cry:')
        await asyncio.sleep(sleep * 3)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
        return

    non_word_re = re.compile('\W')
    word = message.content.lstrip('>').strip().lower()
    word = non_word_re.sub('', word)
    posted_words = event_db.col_values(3)

    # returns None, None if unable to parse time
    passed, time_wait = time.check_delay(latest_ts, 10)

    if word not in valid_words:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, chữ không có trong từ điển tiếng Anh, vui lòng sử dụng tiếng Anh.')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
    elif message.author.id == latest_uid:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, vui lòng đợi người khác nối chữ của mình nhé!')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
    elif passed is False:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, vui lòng đợi thêm {time_wait} giây nữa.')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
    elif latest_word and word[0] != latest_word[-1]:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, vui lòng chọn chữ bắt đầu với ký tự `{latest_word[-1].upper()}`.')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)
    elif word in posted_words:
        failed_note = await bot.send_message(
            channel,
            f'{message.author.mention}, đã có người sử dụng chữ này. Vui lòng chọn chữ khác.')
        await asyncio.sleep(sleep)
        await bot.delete_message(message)
        await bot.delete_message(failed_note)

    # 'passed' is True, or 'passed' is None, or passed the above tests
    else:
        now = datetime.now()
        event_db.insert_row([message.author.id, message.author.name, word, str(now)], index=2)
        success_note = await bot.send_message(
            channel,
            f'{message.author.mention}, chữ hợp lệ. Xin cảm ơn đã tham gia!')
        await asyncio.sleep(sleep)
        await bot.delete_message(success_note)
