#!/usr/bin/env python

import redis
import time

command_groups = {
    'GetTypeCmds': ['get','getbit','getrange','getset','mget','hget','hgetall','hmget'],
    'SetTypeCmds': ['set','setbit','setex','setnx','setrange','mset','msetnx','psetnx',
                    'hmset','hset','hsetnx','lset'],
    'KeyBasedCmds': ['zdel','dump','exists','expire','expireat','keys','move','persist', 'pexpire','pexpireat','pttl','rename','renamenx','restore','ttl','type','append','bitcount','bitop','bitpos','decr','decrby','get','getbit','getrange','getset','incr','incrby','incrbyfloat','mget','mset','msetnx','psetnx','set','setbit','setex','setnx','setrange','strlen','hdel','hexists','hget','hgetall','hincrby','hincrbyfloat','hkeys','hlen','hmget','hmset','hset','hsetnx','hvals','blpop', 'brpop','lindex','linsert','llen','lpop','lpush','lpushx','lrange', 'lrem','lset','ltrim','rpop','rpush','rpushx','sadd','scard','sdiff','sdiffstore','sinter','sinterstore','sismember','smembers','spop','srandmember','srem','sunion','sunionstore', 'sscan','zadd','zcard','zcount','zincrby','zinterstore','zlexcount','zrange','zrangebylex','zrangebyscore','zrank','zrem','zremrangebylex','zremrangebyrank','zremrangebyscore','zrevrange','zrevrangebyscore','zrevrank','zscore','zunionstore','zscan','pfadd','pfcount','pfmerge','watch','eval','evalsha'],
    'StringBasedCmds': ['append','bitcount','bitop','bitpos','decr','decrby','get','getbit', 'getrange','getset','incr','incrby','incrbyfloat','mget','mset', 'msetnx','psetnx','set','setbit','setex','setnx','setrange','strlen'],

    'HashBasedCmds': ['hdel','hexists','hget','hgetall','hincrby','hincrbyfloat','hkeys', 'hlen','hmget','hmset','hset','hsetnx','hvals','hscan'],

    'ListBasedCmds': ['blpop','brpop','brpoplpush','lindex','linsert','llen','lpop','lpush', 'lpushx','lrange','lrem','lset','ltrim','rpop','rpoplpush','rpush', 'rpushx'],

    'SetBasedCmds': ['sadd','scard','sdiff','sdiffstore','sinter','sinterstore','sismember', 'smembers','smove','spop','srandmember','srem','sunion','sunionstore', 'sscan'],

    'SortedSetBasedCmds': ['zadd','zcard','zcount','zincrby','zinterstore','zlexcount','zrange','zrangebylex','zrangebyscore','zrank','zrem','zremrangebylex','zremrangebyrank','zremrangebyscore','zrevrange','zrevrangebyscore','zrevrank','zscore','zunionstore','zscan'],

    'HyperLogLogBasedCmds': ['pfadd','pfcount','pfmerge'],

    'ScriptBasedCmds': ['eval','evalsha']
}

def collect_redis_info():
    r = redis.StrictRedis('localhost', port=6379, db=0)
    info = r.info()
    cmd_info = r.info('commandstats')

    return dict(info.items() + cmd_info.items())

if __name__ == '__main__':
    count_keys = [
       'TotalCmds',
       'BytesIn',
       'BytesOut',
       'Reclaimed',
       'Evictions',
       'CacheHits',
       'CacheMisses',
       'UsedCPUsys',
       'UsedCPUuser',
       'UsedCPUsyschildren',
       'UsedCPUuserchildren',
       'GetTypeCmds',
       'SetTypeCmds',
       'KeyBasedCmds',
       'StringBasedCmds',
       'HashBasedCmds',
       'ListBasedCmds',
       'SetBasedCmds',
       'SortedSetBasedCmds',
       'HyperLogLogBasedCmds',
       'ScriptBasedCmds'
    ]
    redis_data = collect_redis_info()
    count_metrics = {
        'CurrConnections': redis_data['connected_clients'],
        'CurrItems': redis_data['db0']['keys'],
        'UsedMem': redis_data['used_memory'],
        'UsedMemRss': redis_data['used_memory_rss'],
        'MemFrag': redis_data['mem_fragmentation_ratio'],
        'TotalCmds': redis_data['total_commands_processed'],
        'BytesIn': redis_data['total_net_input_bytes'],
        'BytesOut': redis_data['total_net_output_bytes'],
        'Reclaimed': redis_data['expired_keys'],
        'Evictions': redis_data['evicted_keys'],
        'CacheHits': redis_data['keyspace_hits'],
        'CacheMisses': redis_data['keyspace_misses'],
        'UsedCPUsys': redis_data['used_cpu_sys'],
        'UsedCPUuser': redis_data['used_cpu_user'],
        'UsedCPUsyschildren': redis_data['used_cpu_sys_children'],
        'UsedCPUuserchildren': redis_data['used_cpu_user_children']
    }
    for command_group, commands in command_groups.items():
       count_metrics[command_group] = 0
       for command in commands:
           key = 'cmdstat_' + command
           if key in redis_data:
               count_metrics[command_group] += redis_data[key]['calls']
 
    usable_count_metrics = count_metrics
    time.sleep(1)
    while True:
        redis_data = collect_redis_info()

        old_count_metrics = count_metrics
        count_metrics = {
            'CurrConnections': redis_data['connected_clients'],
            'CurrItems': redis_data['db0']['keys'],
            'UsedMem': redis_data['used_memory'],
            'UsedMemRss': redis_data['used_memory_rss'],
            'MemFrag': redis_data['mem_fragmentation_ratio'],
            'TotalCmds': redis_data['total_commands_processed'],
            'BytesIn': redis_data['total_net_input_bytes'],
            'BytesOut': redis_data['total_net_output_bytes'],
            'Reclaimed': redis_data['expired_keys'],
            'Evictions': redis_data['evicted_keys'],
            'CacheHits': redis_data['keyspace_hits'],
            'CacheMisses': redis_data['keyspace_misses'],
            'UsedCPUsys': redis_data['used_cpu_sys'],
            'UsedCPUuser': redis_data['used_cpu_user'],
            'UsedCPUsyschildren': redis_data['used_cpu_sys_children'],
            'UsedCPUuserchildren': redis_data['used_cpu_user_children']
        }

        for command_group, commands in command_groups.items():
            count_metrics[command_group] = 0
            for command in commands:
                key = 'cmdstat_' + command
                if key in redis_data:
                    count_metrics[command_group] += redis_data[key]['calls']


        for key in count_keys:
            if key in usable_count_metrics:
                usable_count_metrics[key] = count_metrics[key]- old_count_metrics[key]
        

        for items in usable_count_metrics:
          print(items, usable_count_metrics[items])
        print('\n')

        time.sleep(1)

