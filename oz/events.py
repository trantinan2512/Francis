import asyncio
import re
import json
from datetime import datetime
from pprint import pprint
from utils import time
from gspread.exceptions import APIError
import config


async def match_word_event(message, channel, bot, event_db, valid_words, sleep=5):

    non_word_re = re.compile('\W')
    word = message.content.lstrip('>').strip().lower()
    word = non_word_re.sub('', word)

    with open(config.BASE_DIR + '/oz/wm_message_check.json') as infile:
        message_check = json.load(infile)

    # get all the necessary info
    latest_post = message_check.get('latest_post')
    if latest_post:
        latest_uid, latest_word, latest_ts = latest_post['uid'], latest_post['word'], latest_post['ts']
    else:
        latest_uid, latest_word, latest_ts = None, None, None

    latest_message = message_check.get('latest_message')
    if latest_message:
        latest_msg_uid, latest_msg_word, latest_msg_ts = latest_message['uid'], latest_message['word'], latest_message['ts']
    else:
        latest_msg_uid, latest_msg_word, latest_msg_ts = None, None, None

    # then overwrite new message
    with open(config.BASE_DIR + '/oz/wm_message_check.json', 'w') as outfile:

        now = datetime.now()
        lm = {
            'latest_message': {
                'uid': message.author.id,
                'word': word,
                'ts': str(now)
            }
        }
        message_check.update(lm)
        # print(new_data)
        json.dump(message_check, outfile)

    # returns None, None if unable to parse time
    latest_post_passed, latest_post_time_wait = time.check_delay(latest_ts, 10)

    latest_msg_passed, latest_msg_time_wait = time.check_delay(latest_msg_ts, 3)

    # spam checker
    if word == latest_msg_word and message.author.id == latest_msg_uid and latest_msg_passed is False:
        await send_notification(
            bot, channel, message,
            f'{message.author.mention}, vui lòng không spam. Tin nhắn của bạn sẽ không được chấp nhận trong vòng **3 giây**.')

    # same person checker
    elif message.author.id == latest_uid:
        await send_notification(
            bot, channel, message,
            f'{message.author.mention}, vui lòng đợi người khác nối chữ của mình nhé!')

    # correct starting letter checker
    elif latest_word and word[0] != latest_word[-1]:
        await send_notification(
            bot, channel, message,
            f'{message.author.mention}, vui lòng chọn chữ bắt đầu với ký tự `{latest_word[-1].upper()}`.')

    # delay checker
    elif latest_post_passed is False:
        await send_notification(
            bot, channel, message,
            f'{message.author.mention}, vui lòng đợi thêm {latest_post_time_wait} giây nữa.')

    # valid English word checker
    elif word not in valid_words:
        await send_notification(
            bot, channel, message,
            f'{message.author.mention}, chữ không có trong từ điển tiếng Anh, vui lòng sử dụng tiếng Anh.')

    # now Google API call
    else:
        # send error if there's an API exception
        try:
            posted_words = event_db.col_values(3)

        except APIError:
            await send_notification(
                bot, channel, message,
                f'Em mệt quá, cho em nghỉ xíu nha :cry:')
            return

        # already present word checker
        if word in posted_words:
            await send_notification(
                bot, channel, message,
                f'{message.author.mention}, đã có người sử dụng chữ này. Vui lòng chọn chữ khác.')

        # passed the above tests, write to database
        else:
            now = datetime.now()
            event_db.insert_row([message.author.id, message.author.name, word, str(now)], index=2)
            latest_post = {
                'latest_post': {
                    'uid': message.author.id,
                    'word': word,
                    'ts': str(now)
                }
            }
            # update the wm_message_check.json file
            with open(config.BASE_DIR + '/oz/wm_message_check.json', 'w') as outfile:
                message_check.update(latest_post)
                json.dump(message_check, outfile)

            await send_notification(
                bot, channel, message,
                f'{message.author.mention}, chữ hợp lệ. Xin cảm ơn đã tham gia!',
                delete=False)


async def send_notification(bot, channel, message, noti_message, sleep=5, delete=True):
    note = await bot.send_message(channel, noti_message)
    await asyncio.sleep(sleep)
    if delete is True:
        await bot.delete_message(message)
    await bot.delete_message(note)
