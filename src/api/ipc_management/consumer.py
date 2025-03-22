import pika

class Consumer:
    def __init__(self):
        pass
    def connect(self):
        connection = pika.BlockingConnection('localhost:5672')
        channel = connection.channel()