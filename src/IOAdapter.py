import json
from datetime import datetime
import sqlite3


class CommandLineIO:
    async def request(self):
        return input("You: ")

    async def reply(self, reply):
        print("GloBot 🌱: " + reply)


class WSIO:
    def __init__(self, ws):
        self.ws = ws

    async def request(self):
        return await self.ws.recv()

    async def reply(self, reply):
        return await self.ws.send(reply)


class FileLoggedIO:
    def __init__(self, logger, conversation_id, user_id, bot_id, sub_io):
        self.logger = logger
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.bot_id = bot_id
        self.sub_io = sub_io
        self.sequence_number = 0

    async def request(self):
        request = await self.sub_io.request()
        self.logger.log_file.write(json.dumps({'conversation': self.conversation_id,
                                               'message': request,
                                               'speaker': 'user/' + self.user_id,
                                               'timestamp': datetime.now().isoformat(),
                                               'sequence': self.sequence_number}) + '\n')
        self.sequence_number += 1
        return request

    async def reply(self, reply):
        self.logger.log_file.write(json.dumps({'conversation': self.conversation_id,
                                               'message': reply,
                                               'speaker': 'bot/' + self.bot_id,
                                               'timestamp': datetime.now().isoformat(),
                                               'sequence': self.sequence_number}) + '\n')
        self.sequence_number += 1
        await self.sub_io.reply(reply)


class FileLogger:
    def __init__(self, path):
        self.log_file = open(path, "a+", buffering=1)

    def makeIO(self, conversation_id, user_id, bot_id, sub_io):
        return FileLoggedIO(self, conversation_id, user_id, bot_id, sub_io)

    def close(self):
        self.log_file.close()


class SQLiteLoggedIO:
    def __init__(self, logger, conversation_id, user_id, bot_id, sub_io):
        self.logger = logger
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.bot_id = bot_id
        self.sub_io = sub_io
        self.sequence_number = 0

    async def request(self):
        request = await self.sub_io.request()
        self.logger.conn.execute("""insert into messages (conversation, sequence, message, speaker, timestamp)
                                    values (?,?,?,?,?)""",
                                 (self.conversation_id,
                                  self.sequence_number,
                                  request,
                                  'user/' + self.user_id,
                                  datetime.now().isoformat()))
        self.logger.conn.commit()
        self.sequence_number += 1
        return request

    async def reply(self, reply):
        self.logger.conn.execute("""insert into messages (conversation, sequence, message, speaker, timestamp)
                                    values (?,?,?,?,?)""",
                                 (self.conversation_id,
                                  self.sequence_number,
                                  reply,
                                  'bot/' + self.bot_id,
                                  datetime.now().isoformat()))
        self.logger.conn.commit()
        self.sequence_number += 1
        await self.sub_io.reply(reply)


class SQLiteLogger:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.executescript("""
            create table if not exists messages(
                conversation text,
                sequence int,
                message text,
                speaker text,
                timestamp datetime,
                primary key(conversation,sequence)
            );
            """)
        self.conn.commit()

    def makeIO(self, conversation_id, user_id, bot_id, sub_io):
        return SQLiteLoggedIO(self, conversation_id, user_id, bot_id, sub_io)

    def close(self):
        self.conn.close()
