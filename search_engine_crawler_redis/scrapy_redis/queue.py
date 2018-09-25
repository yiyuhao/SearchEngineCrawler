from scrapy.utils.reqser import request_to_dict, request_from_dict

from . import picklecompat


class Base(object):
    """Per-spider base queue class"""

    def __init__(self, server, spider, key, serializer=None):
        """Initialize per-spider redis queue.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        spider : Spider
            Scrapy spider instance.
        key: str
            Redis key where to put and get messages.
        serializer : object
            Serializer object with ``loads`` and ``dumps`` methods.

        """
        if serializer is None:
            # Backward compatibility.
            # TODO: deprecate pickle.
            serializer = picklecompat
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r"
                            % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
                            % serializer)

        self.server = server
        self.spider = spider
        self.key = key % {'spider': spider.name}
        self.serializer = serializer

    def _encode_request(self, request):
        """Encode a request object"""
        obj = request_to_dict(request, self.spider)
        return self.serializer.dumps(obj)

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""
        obj = self.serializer.loads(encoded_request)
        return request_from_dict(obj, self.spider)

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)


class FifoQueue(Base):
    """Per-spider FIFO queue"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return self._decode_request(data)


class PriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""

    def __init__(self, *args, **kwargs):
        super(PriorityQueue, self).__init__(*args, **kwargs)
        self.requests = {}
        self.cur_request_id = None

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def _record_request_push(self, request_id):
        self.requests[request_id] = self.requests.get(request_id, 0) + 1

    def _record_request_pop(self, request_id):
        if request_id not in self.requests:
            return
        after_num = self.requests[request_id] - 1
        self.requests[request_id] = after_num

        if after_num <= 0:
            del self.requests[request_id]

    @property
    def next_request_id(self):
        if not self.requests:
            return None

        if self.cur_request_id is None:
            result = next(iter(self.requests.keys()))  # first elem of self.requests
        else:
            found = False
            for id_ in self.requests.keys():
                if found is True:
                    result = id_
                    break
                if self.cur_request_id == id_:
                    found = True
            else:
                result = next(iter(self.requests.keys()))
        return result

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        self.server.execute_command('ZADD', self.key, score, data)
        self._record_request_push(request.meta['search_request_id'])  # record then fetch one by one from different requests

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        # use atomic range/remove using multi/exec
        next_id = self.next_request_id

        if next_id:
            all_requests = self.server.zrange(self.key, 0, -1)
            for redis_request in all_requests:
                id_ = self.serializer.loads(redis_request)['meta']['search_request_id']
                if id_ == next_id:
                    print(f'pop a request {id_}, remain list: {self.requests}')
                    self.cur_request_id = id_
                    self._record_request_pop(id_)
                    self.server.zrem(self.key, redis_request)
                    return self._decode_request(redis_request)

        # not find
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            id_ = self.serializer.loads(results[0])['meta']['search_request_id']
            print(f'pop a request {id_}, remain list: {self.requests}')
            self.cur_request_id = id_
            self._record_request_pop(id_)
            return self._decode_request(results[0])


class LifoQueue(Base):
    """Per-spider LIFO queue."""

    def __len__(self):
        """Return the length of the stack"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.blpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)

        if data:
            return self._decode_request(data)


# TODO: Deprecate the use of these names.
SpiderQueue = FifoQueue
SpiderStack = LifoQueue
SpiderPriorityQueue = PriorityQueue
