import redis        
from redis.client import parse_info
import time

class Monitor():
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self.connection = None

    def __del__(self):
        try:
            self.reset()
        except:
            pass

    def reset(self):
        if self.connection:
            self.connection_pool.release(self.connection)
            self.connection = None

    def monitor(self):
        if self.connection is None:
            self.connection = self.connection_pool.get_connection(
                'info', None)
        self.connection.send_command("info")
        info = parse_info(self.connection.read_response())
        return info

    def monitor_commandstats(self):
        if self.connection is None:
            self.connection = self.connection_pool.get_connection(
                'info commandstats', None)
        self.connection.send_command("info commandstats")
        info = parse_info(self.connection.read_response())
        return info


    def parse_response(self):
        return self.connection.read_response()

    def listen(self):
        while True:
            yield self.parse_response()

if  __name__ == '__main__':
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    monitor = Monitor(pool)
    info = monitor.monitor()
    time.sleep(1)

    template = "%14s%14s%14s%14s%18s%14s%14s%14s%14s%14s%14s%14s"
    header = ('cpusys', 'conclient', 'conslave', 'usedmem', 'usedcpuchildren', 'commands', 'usedmemrss', 'conrecv', 'cpuusr', 'changes', 'memfrag', 'keyspace')

    cpusys = float(info['used_cpu_sys'])
    conclient = int(info['connected_clients'])
    conslave = int(info['connected_slaves'])
    usedmem = int(info['used_memory'])
    usedcpuchildren = float(info['used_cpu_user_children'])
    commands = int(info['total_commands_processed'])
    usedmemrss = int(info['used_memory_rss'])
    conrecv = int(info['total_connections_received'])
    cpuusr = float(info['used_cpu_user'])
    changes = int(info['changes_since_last_save'])
    memfrag = float(info['mem_fragmentation_ratio'])
    keyspace = int(info['keyspace_hits'])

    ii = 0
    while True:
        #old_info = info
        info = monitor.monitor()
        commandstats = monitor.monitor_commandstats()
        #for i in info:
        #    print "{} : {}".format(i, info[i])

        oldcpusys = cpusys
        oldconclient = conclient
        oldconslave = conslave
        oldusedcpuchildren = usedcpuchildren
        oldcommands = commands
        oldconrecv = conrecv
        oldcpuusr = cpuusr
        oldchanges = changes
        oldkeyspace = keyspace

        
        cpusys = float(info['used_cpu_sys'])
        conclient = int(info['connected_clients'])
        conslave = int(info['connected_slaves'])
        usedmem = int(info['used_memory'])
        usedcpuchildren = float(info['used_cpu_user_children'])
        commands = int(info['total_commands_processed'])
        usedmemrss = int(info['used_memory_rss'])
        conrecv = int(info['total_connections_received'])
        cpuusr = float(info['used_cpu_user'])
        changes = int(info['changes_since_last_save'])
        memfrag = float(info['mem_fragmentation_ratio'])
        keyspace = int(info['keyspace_hits'])

        datastr = "cpusys - oldcpusys, conclient - oldconclient, conslave - oldconslave, usedmem, usedcpuchildren - oldusedcpuchildren, commands - oldcommands, usedmemrss, conrecv - oldconrecv, cpuusr - oldcpuusr, changes - oldchanges, memfrag, keyspace - oldkeyspace"

        if (ii % 25 == 0):
            print template % header
        print template % (eval(datastr))

        print('\n')

        ii += 1
        time.sleep(1)
