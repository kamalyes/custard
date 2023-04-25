import random
import string
import sys
from custard.rediscluster import RedisCluster

startup_nodes = [{"host": "127.0.0.1", "port": "7000"}]

# Note: decode_responses must be set to True when used with python3
rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

# 10 batches
batch_set = {i: [] for i in range(0, 16388)}

# Do 100000 slot randos in each block
for j in range(0, 100000):
    random_string = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(5)
    )

    keyslot = rc.connection_pool.nodes.keyslot(random_string)

    # batch_set.setdefault(keyslot)
    batch_set[keyslot].append(random_string)

for i in range(0, 16388):
    if len(batch_set[i]) > 0:
        print(i, ":", batch_set[i])
        sys.exit(0)
