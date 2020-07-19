import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

host = "localhost"
port = "6379"

r.hmset('thread', {'topic': 'upgrades', 'step': 1})

print(r.hgetall('thread'))

