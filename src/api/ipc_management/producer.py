from enum import Enum

import pika


class QueueType(Enum):
    GOGET = "GoGet"

class Producer:
    def __init__(self, qtype: QueueType):
        self.type = qtype
        self.connection = None
        self.channel = None
        pass
    def connect(self):
        self.connection = pika.BlockingConnection('localhost:5672')
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.type.value)
    def send(self, to_send: bytes):
        if not self.channel:
            raise ValueError(f"The channel hasn't been defined yet for queue type: {self.type.value}")
        self.channel.basic_publish(
            exchange='',
            routing_key=self.type.value,
            body=to_send
        )