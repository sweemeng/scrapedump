import redis


class PubSub(object):
    def __init__(self,channel):
        self.channel = channel
        self.redis = redis.Redis()
        self.pubsub = self.redis.pubsub()

    def subscribe(self):
        self.pubsub.subscribe(self.channel)
        msg = self.pubsub.listen()
        while True:
            yield msg.next()['data']

    def publish(self,data):
        self.redis.publish(self.channel,data)
