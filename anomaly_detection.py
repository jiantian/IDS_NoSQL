#!/usr/bin/python
#

import datetime, os, time, sys, random
import optparse
import pymongo
import redis
import commands
from pymongo import MongoClient

from optparse import OptionParser
from knn import KNN
from perceptron import Perceptron
from batchexecutor import ClassifierFlags, BatchExecutor

class DetectionFramework:

    def __init__(self, db_type, hostname, port, algorithm, batchfile, sleep_interval):
        self.db_type = db_type
        self.hostname = hostname 
        self.algorithm = algorithm
        self.batchfile = batchfile
        self.sleep_interval = sleep_interval
        self.do_perceptron_learn = False
 
        if db_type == 'mongodb' or db_type == '1':
            print("MongoDB Database")

            if port == "":
                port="27017"
            self.port = port
            client = MongoClient("{}:{}".format(hostname, port))
            self.db = client.ycsb

            #all of the metrics to be used
            self.metric_groups = {
                'opcounters': ['query', 'insert', 'update', 'delete', 
                               'getmore', 'command', 'queryCpuTime',
                               'insertCpuTime', 'updateCpuTime',
                               'deleteCpuTime', 'getMoreCpuTime',
                               'commandCpuTime'],
                'connections': ['current'],
                'indexCounters': ['accesses', 'hits', 'misses'], 
                'network': ['bytesIn', 'bytesOut', 'numRequests'],
                #'mem': ['resident', 'virtual', 'mapped'],
                #'collections': [],
                'objects': [],
                #'avgObjSize': [],
                #'dataSize': [],
                #'storageSize': [], 
                #'fileSize': [],
                
            }

            #all of the metrics that are aggregated that we would like to
            #be in per second values
            self.counter_keys =  {
                'opcounters': ['query', 'insert', 'update', 'delete', 
                               'getmore', 'command', 'queryCPU',
                               'queryCpuTime', 'insertCpuTime',
                               'updateCpuTime', 'deleteCpuTime',
                               'getMoreCpuTime', 'commandCpuTime'],
                'indexCounters': ['accesses', 'hits', 'misses'], 
                'network': ['bytesIn', 'bytesOut', 'numRequests'],
                'collections': [],
                'objects': [],
                'dataSize': [],
                'storageSize': [], 
                'fileSize': [],

            }
        elif db_type == 'redis' or db_type == '2':
            print("Redis Database")

            if port == "":
                port="6379"
            self.port = port
            self.db = redis.StrictRedis(hostname, port, db=0)

            #all of the metrics to be used
            self.metric_groups = {
                'connected_clients': [],
                #'used_memory': [],
                #'used_memory_rss': [],
                #'mem_fragmentation_ratio': [],
                'total_commands_processed': [],
                'total_net_input_bytes': [],
                'total_net_output_bytes': [],
                #'expired_keys': [],
                #'evicted_keys': [],
                'keyspace_hits': [],
                'keyspace_misses': [],
                'used_cpu_sys': [],
                'used_cpu_user': [],
                #'used_cpu_sys_children': [],
                #'used_cpu_user_children': [],
                'db0': ['keys'],

                'GetTypeCmds': ['cmdstat_get','cmdstat_getbit',
                                'cmdstat_getrange','cmdstat_getset',
                                'cmdstat_mget','cmdstat_hget',
                                'cmdstat_hgetall','cmdstat_hmget'],

                'SetTypeCmds': ['cmdstat_set','cmdstat_setbit',
                                'cmdstat_setex','cmdstat_setnx',
                                'cmdstat_setrange',
                                'cmdstat_mset','cmdstat_msetnx',
                                'cmdstat_psetnx','cmdstat_hmset',
                                'cmdstat_hset','cmdstat_hsetnx',
                                'cmdstat_lset'],

                'KeyBasedCmds': ['cmdstat_zdel','cmdstat_dump',
                                 'cmdstat_exists','cmdstat_expire',
                                 'cmdstat_expireat','cmdstat_keys',
                                 'cmdstat_move','cmdstat_persist', 
                                 'cmdstat_pexpire','cmdstat_pexpireat',
                                 'cmdstat_pttl','cmdstat_rename',
                                 'cmdstat_renamenx','cmdstat_restore',
                                 'cmdstat_ttl','cmdstat_type',
                                 'cmdstat_append','cmdstat_bitcount',
                                 'cmdstat_bitop','cmdstat_bitpos',
                                 'cmdstat_decr','cmdstat_decrby',
                                 'cmdstat_get','cmdstat_getbit',
                                 'cmdstat_getrange','cmdstat_getset',
                                 'cmdstat_incr','cmdstat_incrby',
                                 'cmdstat_incrbyfloat','cmdstat_mget',
                                 'cmdstat_mset','cmdstat_msetnx',
                                 'cmdstat_psetnx','cmdstat_set',
                                 'cmdstat_setbit','cmdstat_setex',
                                 'cmdstat_setnx','cmdstat_setrange',
                                 'cmdstat_strlen','cmdstat_hdel',
                                 'cmdstat_hexists','cmdstat_hget',
                                 'cmdstat_hgetall','cmdstat_hincrby',
                                 'cmdstat_hincrbyfloat','cmdstat_hkeys',
                                 'cmdstat_hlen','cmdstat_hmget',
                                 'cmdstat_hmset','cmdstat_hset',
                                 'cmdstat_hsetnx','cmdstat_hvals',
                                 'cmdstat_blpop','cmdstat_brpop',
                                 'cmdstat_lindex','cmdstat_linsert',
                                 'cmdstat_llen','cmdstat_lpop',
                                 'cmdstat_lpush','cmdstat_lpushx',
                                 'cmdstat_lrange', 'cmdstat_lrem',
                                 'cmdstat_lset','cmdstat_ltrim',
                                 'cmdstat_rpop','cmdstat_rpush',
                                 'cmdstat_rpushx','cmdstat_sadd',
                                 'cmdstat_scard','cmdstat_sdiff',
                                 'cmdstat_sdiffstore','cmdstat_sinter',
                                 'cmdstat_sinterstore','cmdstat_sismember',
                                 'cmdstat_smembers','cmdstat_spop',
                                 'cmdstat_srandmember','cmdstat_srem',
                                 'cmdstat_sunion','cmdstat_sunionstore',
                                 'cmdstat_sscan','cmdstat_zadd',
                                 'cmdstat_zcard','cmdstat_zcount',
                                 'cmdstat_zincrby','cmdstat_zinterstore',
                                 'cmdstat_zlexcount','cmdstat_zrange',
                                 'cmdstat_zrangebylex',
                                 'cmdstat_zrangebyscore','cmdstat_zrank',
                                 'cmdstat_zrem','cmdstat_zremrangebylex',
                                 'cmdstat_zremrangebyrank',
                                 'cmdstat_zremrangebyscore',
                                 'cmdstat_zrevrange',
                                 'cmdstat_zrevrangebyscore',
                                 'cmdstat_zrevrank','cmdstat_zscore',
                                 'cmdstat_zunionstore','cmdstat_zscan',
                                 'cmdstat_pfadd','cmdstat_pfcount',
                                 'cmdstat_pfmerge','cmdstat_watch',
                                 'cmdstat_eval','cmdstat_evalsha'],

                'StringBasedCmds': ['cmdstat_append','cmdstat_bitcount',
                                    'cmdstat_bitop','cmdstat_bitpos',
                                    'cmdstat_decr','cmdstat_decrby',
                                    'cmdstat_get','cmdstat_getbit', 
                                    'cmdstat_getrange','cmdstat_getset',
                                    'cmdstat_incr','cmdstat_incrby',
                                    'cmdstat_incrbyfloat','cmdstat_mget',
                                    'cmdstat_mset', 'cmdstat_msetnx',
                                    'cmdstat_psetnx','cmdstat_set',
                                    'cmdstat_setbit','cmdstat_setex',
                                    'cmdstat_setnx','cmdstat_setrange',
                                    'cmdstat_strlen'],
            
                'HashBasedCmds': ['cmdstat_hdel','cmdstat_hexists',
                                  'cmdstat_hget','cmdstat_hgetall',
                                  'cmdstat_hincrby','cmdstat_hincrbyfloat',
                                  'cmdstat_hkeys', 'cmdstat_hlen',
                                  'cmdstat_hmget','cmdstat_hmset',
                                  'cmdstat_hset','cmdstat_hsetnx',
                                  'cmdstat_hvals','cmdstat_hscan'],
            
                'ListBasedCmds': ['cmdstat_blpop','cmdstat_brpop',
                                  'cmdstat_brpoplpush','cmdstat_lindex',
                                  'cmdstat_linsert','cmdstat_llen',
                                  'cmdstat_lpop','cmdstat_lpush', 
                                  'cmdstat_lpushx','cmdstat_lrange',
                                  'cmdstat_lrem','cmdstat_lset',
                                  'cmdstat_ltrim','cmdstat_rpop',
                                  'cmdstat_rpoplpush','cmdstat_rpush', 
                                  'cmdstat_rpushx'],
            
                'SetBasedCmds': ['cmdstat_sadd','cmdstat_scard',
                                 'cmdstat_sdiff','cmdstat_sdiffstore',
                                 'cmdstat_sinter','cmdstat_sinterstore',
                                 'cmdstat_sismember','cmdstat_smembers',
                                 'cmdstat_smove','cmdstat_spop',
                                 'cmdstat_srandmember',
                                 'cmdstat_srem','cmdstat_sunion',
                                 'cmdstat_sunionstore', 'cmdstat_sscan'],
            
                'SortedSetBasedCmds': ['cmdstat_zadd','cmdstat_zcard',
                                       'cmdstat_zcount','cmdstat_zincrby',
                                       'cmdstat_zinterstore',
                                       'cmdstat_zlexcount','cmdstat_zrange',
                                       'cmdstat_zrangebylex',
                                       'cmdstat_zrangebyscore',
                                       'cmdstat_zrank','cmdstat_zrem',
                                       'cmdstat_zremrangebylex',
                                       'cmdstat_zremrangebyrank',
                                       'cmdstat_zremrangebyscore',
                                       'cmdstat_zrevrange',
                                       'cmdstat_zrevrangebyscore',
                                       'cmdstat_zrevrank','cmdstat_zscore',
                                       'cmdstat_zunionstore',
                                       'cmdstat_zscan'],
            
                'HyperLogLogBasedCmds': ['cmdstat_pfadd','cmdstat_pfcount',
                                         'cmdstat_pfmerge'],
            
                'ScriptBasedCmds': ['cmdstat_eval','cmdstat_evalsha'],
            }
      
            #all of the metrics that are aggregated that we would like to
            #be in per second values
            self.counter_keys = {
                'total_commands_processed': [],
                'total_net_input_bytes': [],
                'total_net_output_bytes': [],
                'expired_keys': [],
                'evicted_keys': [],
                'keyspace_hits': [],
                'keyspace_misses': [],
                'used_cpu_sys': [],
                'used_cpu_user': [],
                'used_cpu_sys_children': [],
                'used_cpu_user_children': [],
                'db0': ['keys'],
                'GetTypeCmds': [],
                'SetTypeCmds': [],
                'KeyBasedCmds': [],
                'StringBasedCmds': [],
                'HashBasedCmds': [],
                'ListBasedCmds': [],
                'SetBasedCmds': [],
                'SortedSetBasedCmds': [],
                'HyperLogLogBasedCmds': [],
                'ScriptBasedCmds': [],

            }
        else:
            print('Invalid DB choice')
            self.metric_groups = {}
            self.counter_keys = {}

    #collect metric data from the database itself
    def getData(self):
        if self.db_type == 'mongodb' or self.db_type == '1':
            info = (self.db.command({"serverStatus" : 1}))
            stats_info = (self.db.command({"dbstats" : 1}))
            return dict(info.items() + stats_info.items())
        elif self.db_type == 'redis' or self.db_type == '2':
            r = self.db
            info = r.info()
            cmd_info = r.info('commandstats')
            return dict(info.items() + cmd_info.items())
        else:
            return 0

    def getTrainOrTest(self):
        traintest = 0
        while True:
            traintest = raw_input("Choose Training/Testing Option \
                                   \n1) Normal Training  \
                                   \n2) Anomaly Training \
                                   \n3) Testing\n") 
            if traintest != '1' and traintest != '2' and traintest != '3':
                print("Invalid Choice. Choose Again")
            else:
                if traintest != '3':
                    duration = input("For how many seconds?\n")
                    if duration > 0:
                        break
                    else:
                        print("Duration must be greater than 0")
                else:
                    duration =  input("For how many seconds? (-1 for forever)\n")
                    if duration > 0 or duration == -1:
                        break
              

        return traintest, duration
        
   
    #Get the data and run the detection algorithm
    def Detection(self):
        if (db_type != 'mongodb' and db_type != '1' and 
            db_type != 'redis' and db_type != '2'):
            return

        if self.algorithm == 'knn' or self.algorithm == '1':
            print("K nearest neighbor algorithm")
            detection_algorithm = KNN()
        elif self.algorithm == 'perceptron' or self.algorithm == '2':
            detection_algorithm = Perceptron()
            self.do_perceptron_learn = True # only do once before the testing!
            #print('Invalid algorithm. SVM not yet supported')
            #return
        else:
            print('Invalid algorithm selection')
            return
    
        have_batchfile = len(self.batchfile) != 0
        if have_batchfile:
            batchex = BatchExecutor(self.batchfile, detection_algorithm,
                                    self.do_perceptron_learn,
                                    hostname=self.hostname, port=27017)
            batchex.start()

        metric_groups = self.metric_groups
        counter_keys = self.counter_keys

        data = []
        new_metrics = {}
        old_metrics = {}
        anomaly_metrics = {}
        sleep = self.sleep_interval
        fp = open('./out.txt', 'a+')

        # just run forever until ctrl-c (in non-batch mode) or run until the
        # batch executor finishes (in batch mode)
        while True:
            if have_batchfile:
                allDone, duration = batchex.wait_for_measure_to_be_ready_all_done_or_failed()
                if allDone:
                    break
                if duration == None:
                    print("FATAL ERROR: Batch execution failed!")
                    break
            else:
                traintest, duration = self.getTrainOrTest()

            #train/test for a set duration
            if duration == -1:
                print("Running forever") 
                forever = 1
            else:
                if duration == 0.0:
                    raise ValueError("invalid duration")
                print("Running for {} seconds".format(duration))
                forever = 0

            ii = 0
            # fetch the metrics
            data = self.getData()
    
            #Initial block is to set up old_metrics
            #since we only care about the changes in some values, not the 
            # aggregates

            #put all the new metrics in new_metrics
            for metric_group, items in metric_groups.items():
                #If the item is not a list, then take it straight from data
                if not items:
                    try:
                        new_metrics[metric_group] = float(data[metric_group])
                    except KeyError:
                        pass
                else:
                    #set to 0 so that we can recalculate the aggregate values

                    #this is for resetting the values on the subsequent
                    #iteration (e.g. testing -> training)
                    if (metric_group in new_metrics and 
                        metric_group not in data):
                        new_metrics[metric_group] = 0
                        anomaly_metrics[metric_group] = 0

                    #iterate over the list of items
                    for item in items:
                        #if the metric_group is in data, then its items will be
                        #as well
                        if metric_group in data:
                            try:
                                new_metrics[metric_group + item] = float(data[metric_group][item])
                                anomaly_metrics[metric_group + item] = float(data[metric_group][item])
                            except KeyError:
                                pass
                        #if the metric_group isn't in data, but its items are
                        #then aggregate all of the items into the metric_group
                        #This happens in Redis to aggregate all types of
                        #commands together
                        elif item in data:
                            if metric_group not in new_metrics:
                                new_metrics[metric_group] = 0
                                anomaly_metrics[metric_group] = 0
                            try:
                                new_metrics[metric_group] += float(data[item]['calls'])
                                anomaly_metrics[metric_group] += float(data[item]['calls'])
                            except KeyError:
                                pass

            while duration > 0 or forever == 1:
                time.sleep(sleep)
                duration -= sleep
                point = ()

                
                # fetch the metrics
                data = self.getData()

                #put all the new metrics in new_metrics
                for metric_group, items in metric_groups.items():
                    #set old to new so that we can take the difference
                    #between the two measurements 
                    if metric_group in new_metrics:
                        old_metrics[metric_group] = new_metrics[metric_group]
                        new_metrics[metric_group] = 0
                        anomaly_metrics[metric_group] = 0

                    #set to 0 so that we can recalculate the aggregate values
                    #If the item is not a list, then take it straight from data
                    if not items:
                        try:
                            new_metrics[metric_group] = float(data[metric_group])
                            anomaly_metrics[metric_group] = float(data[metric_group])
                        except KeyError:
                            pass

                    else:
                        #iterate over the list of items
                        for item in items:
                            #if the metric_group is in data, then its items 
                            #will be as well
                            if metric_group in data:
                                try:
                                    old_metrics[metric_group + item] = new_metrics[metric_group + item]
                                    new_metrics[metric_group + item] = float(data[metric_group][item])
                                    anomaly_metrics[metric_group + item] = float(data[metric_group][item])
                                except KeyError:
                                    pass
                            #if the metric_group isn't in data, but its items 
                            #are then aggregate all of the items into the 
                            #metric_group
                            #This happens in Redis to aggregate all types of 
                            #commands together
                            elif item in data:
                                try:
                                    new_metrics[metric_group] += float(data[item]['calls'])
                                    anomaly_metrics[metric_group] += float(data[item]['calls'])
                                except KeyError:
                                    pass


                #make per second values for the counters
                for counter_group, items in counter_keys.items():
                    #if the item is not a list, then we can just subtract the
                    #entire counter group. This is in Redis where we aggregate
                    #all command types together
                    if not items:
                        if counter_group in new_metrics:
                            try:
                                anomaly_metrics[counter_group] = (new_metrics[counter_group] - old_metrics[counter_group]) / sleep
                            except KeyError:
                                pass
                    else:
                        #iterate over all items in the list
                        for item in items:
                            if counter_group in data:
                                try:
                                    anomaly_metrics[counter_group+item] = (new_metrics[counter_group+item] - old_metrics[counter_group+item]) / sleep
                                except KeyError:
                                    pass
            
                #create a tuple from the anomaly_metrics dictionary
                #yes I know this is a slow and dumb way to do this
                for items in anomaly_metrics:
                    point += (anomaly_metrics[items],) 
                    sys.stdout.write("{}, {}\n".format(items, anomaly_metrics[items]))
                    if not ii % 100000:
                        #sys.stdout.write("{}, ".format(items))
                        fp.write("{}, ".format(items))
                sys.stdout.write("\n")

                if not ii % 50:
                    print(ii)
                if not ii % 100000:
                    #print('\n')
                    fp.write("\n")
                ii += 1
                            
                #print anomaly_metrics
                #sys.stdout.write("{}\n".format(point))
                fp.write("{}\n".format(point))

                if have_batchfile:
                    batchex.signal_measuring_done(point, duration)
                elif traintest == '1':
                    detection_algorithm.trainSet.append({point:'Normal'})
                    detection_algorithm.size_normal_train += 1
                elif traintest == '2':
                    detection_algorithm.trainSet.append({point:'Anomaly'})
                    detection_algorithm.size_anomaly_train += 1
                elif traintest == '3':
                    #print point
                    if self.do_perceptron_learn == True:	
                        detection_algorithm.preProcess()
                        self.do_perceptron_learn = False
                    label = detection_algorithm.getLabel(point)
                    if label == 'Normal' or label == 0:
                        print 'Normal'
                        #fp.write('Normal\n')
                    elif label == 'Anomaly' or label == 1:
                        print 'Anomaly'
                        #fp.write('Anomaly\n')
                    print('\n')

                fp.flush()



if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--hostname', action="store", dest="hostname",
                      default="localhost")
    parser.add_option('-p', '--port', action="store", dest="port", 
                      default="")
    parser.add_option('-d', '--database', action="store", dest="db_type", 
                      default="")
    parser.add_option('-a', '--algorithm', action="store", 
                      dest="algorithm", default="")
    parser.add_option('-f', '--batchfile', action="store",
                      dest="batchfile", default="")
    parser.add_option('-i', '--sleep-interval', action="store",
                      dest="sleep_interval", default="1")
    options, args = parser.parse_args()
    hostname = options.hostname
    port = options.port
    db_type = options.db_type
    algorithm = options.algorithm
    batchfile = options.batchfile
    try:
        sleep_interval = float(options.sleep_interval)
    except ValueError:
        print "Invalid value for sleep interval!"
        sys.exit(1)

    if db_type == "":
        db_type = raw_input("Please choose a DB\n1) MongoDB\n2) Redis\n")
    if algorithm == "":
        algorithm = raw_input("Please choose a DB\n1) k-Nearest Neighbor\n2) Perceptron\n")
    

    detection = DetectionFramework(db_type, hostname, port, algorithm, batchfile, sleep_interval)
    detection.Detection()

