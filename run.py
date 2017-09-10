import time
import telepot
from datetime import datetime, timedelta
from telepot.loop import MessageLoop
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space)
import storage
import sys


vote_storage = storage.VoteStorage()

week = ['monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday']


class VoteCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(VoteCounter, self).__init__(*args, **kwargs)

        global vote_storage
        self.storage = vote_storage

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if content_type != 'text':
            return

        command = self.get_command(msg)

        if command is None:
            self.sender.sendMessage("Unknown command")
            return

        if command == "/next":
            txt = self.get_text_skip_entities(msg)
            date = self.next_date(txt)
            if date is None:
                self.sender.sendMessage("Unknown date")
            else:
                self.storage.next_event(date)
                self.send_next_date()
            return

        if command == "/when":
            self.send_next_date()
            return

        if command == "/add":
            persons = self.get_persons(msg)
            if persons is not None and len(persons) > 0:
                for p in persons:
                    self.add_user(p)
            else:
                self.add_user(msg["from"])
            return

        if command == "/remove":
            persons = self.get_persons(msg)
            if persons is not None and len(persons) > 0:
                for p in persons:
                    self.remove_user(p)
            else:
                self.remove_user(msg["from"])
            return

        if command == "/who":
            all_p = self.get_players()
            if len(all_p) == 0:
                self.sender.sendMessage("Nobody on {}".format(self.get_fmt_next_date()))
                return
            msg = "There are {0}: \r\n".format(self.format_players_count(len(all_p)))
            for k in all_p:
                p = all_p[k]
                msg += "{0}\r\n".format(self.name(p))
            self.sender.sendMessage(msg)
            return

    def send_next_date(self):
        date = self.storage.get_next_event()
        self.sender.sendMessage("Next game is on " + self.fmt_next_date(date))

    def get_fmt_next_date(self):
        date = self.storage.get_next_event()
        return self.fmt_next_date(date)

    def get_players_count(self):
        return len(self.get_players())

    def format_players_count(self, cnt=None):
        cnt = cnt or self.get_players_count()
        if cnt == 0:
            return "no players"
        if cnt == 1:
            return "1 player"
        return "{0} players".format(str(cnt))

    def get_players(self):
        all_p = self.storage.all()
        if all_p is None:
            return []
        return all_p

    @staticmethod
    def fmt_next_date(date):
        return date.strftime("%A %d. %B %Y")

    def add_user(self, user):
        self.storage.add(user)
        self.sender.sendMessage("{0} will play, there are {1} already"
                                .format(self.name(user), self.format_players_count()))

    def remove_user(self, user):
        self.storage.remove(user)
        self.sender.sendMessage("{0} will not play, there are {1} now"
                                .format(self.name(user), self.format_players_count()))

    @staticmethod
    def name(user):
        first_name = user.get('first_name', "")
        second_name = user.get('last_name', "")
        return "{0} {1}".format(first_name, second_name)

    @staticmethod
    def next_date(day):
        day = day.strip().lower()
        next_event = datetime.now() + timedelta(days=1)
        for i in range(0, 6):
            today_day = next_event.weekday()
            index = week.index(day)
            if today_day == index:
                return next_event
            next_event = next_event + timedelta(days=1)
        return None

    @staticmethod
    def get_text_skip_entities(msg):
        txt = msg["text"]
        if 'entities' not in msg:
            return txt
        entities = msg['entities']
        if len(entities) == 0:
            return txt
        remove_offset = 0
        for t in entities:
            offset = t['offset'] - remove_offset
            length = t['length']
            remove_offset += length
            txt = txt[:offset] + txt[offset + length:]
        return txt

    @staticmethod
    def get_persons(msg):
        result = list()
        if 'entities' not in msg:
            return None
        entities = msg['entities']
        if len(entities) == 0:
            return None
        for entity in entities:
            if entity['type'] == 'text_mention' and 'user' in entity:
                result.append(entity["user"])
        return result

    @staticmethod
    def get_command(msg):
        if 'entities' not in msg:
            return None
        entities = msg['entities']
        if len(entities) == 0:
            return None
        def_command = msg['entities'][0]
        if def_command['type'] != 'bot_command':
            return None
        cmd_start = def_command['offset']
        cmd_length = def_command['length']
        txt = msg["text"]
        cmd_text = txt[cmd_start:cmd_start + cmd_length]
        cmd = cmd_text.split('@')[0]
        return cmd

PROD_TOKEN = "311427299:AAH383yX1vqVsGR_59qJp3bdkTFbrr-UN38"
DEV_TOKEN = "409284378:AAGOvaA_SRaKrbb-gL6z-yWnK3260MTEGyc"
TOKEN = DEV_TOKEN  # by default we have dev token

if len(sys.argv) > 0 and sys.argv[1] == "prod":
    TOKEN = PROD_TOKEN
    print("Bot will start in production mode")
else:
    print("Bot will start in development mode")

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
            per_chat_id(types=['private', 'channel', 'group', 'supergroup']), create_open, VoteCounter, timeout=10),
])
MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)