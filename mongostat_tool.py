#!/usr/bin/python
#

import datetime, os, time, sys, random
import pymongo
import commands
from pymongo import MongoClient

from optparse import OptionParser

class MongoStat:

    def __init__(self, db_name):
        self.db = db_name

    def thetime(self):
        return datetime.datetime.now().strftime("%d-%m-%Y.%H:%M:%S")

    # get the load avg.  needs to be mucked for platforms other than linux
    def getload(self):
      if (sys.platform == 'linux2'):
        cmd = "cat /proc/loadavg"
        out = commands.getstatusoutput(cmd)
        load = out[1].split()[0]
      else:
        load = 0
      return load
         
    def printStats(self):
        data = []
        sleep = 1
        q = 0
        i = 0
        u = 0
        d = 0
        qcpu = 0
        icpu = 0
        ucpu = 0
        dcpu = 0
        ii = 0
        con = 0
        hostname = "localhost"
        idx_b_a = 0
        idx_b_h = 0
        idx_b_m = 0
        new_bytesIn = 0
        new_bytesOut = 0
        new_numRequests = 0
        bytesIn = 0
        bytesOut = 0
        numRequests = 0
        network_skip_flag = 0

        # just run forever until ctrl-c
        while True:
            
            # set previous values before overwriting
            pq = q
            pi = i
            pu = u
            pd = d
            pqcpu = qcpu
            picpu = icpu
            pucpu = ucpu
            pdcpu = dcpu
            pidx_b_a = idx_b_a
            pidx_b_h = idx_b_h
            pidx_b_m = idx_b_m
            
            # fetch the stats
            data = ( self.db.command( { "serverStatus" : 1 } ) )

            res = int(data['mem']['resident'])
            vir = int(data['mem']['virtual'])
            mapd = int(data['mem']['mapped'])

            old_bytesIn = new_bytesIn  
            old_bytesOut = new_bytesOut
            old_numRequests = new_numRequests 

            new_bytesIn = int(data['network']['bytesIn'])
            new_bytesOut = int(data['network']['bytesOut'])
            new_numRequests = int(data['network']['numRequests'])

            if(network_skip_flag == 0):
                network_skip_flag = 1
            else:
              bytesIn = new_bytesIn - old_bytesIn
              bytesOut = new_bytesOut - old_bytesOut
              numRequests = new_numRequests - old_numRequests


            template="%12s%22s%12s%12s%12s%12s"
            header=('hostname', 'time', 'resident','virtual', 'mapped', 'load', 'bytesIn', 'bytesOut', 'numRequests')
            datastr="hostname, self.thetime(),  res, vir, mapd, self.getload(), bytesIn, bytesOut, numRequests"

            if "opcounters" in data:
                q = int(data['opcounters']['query'])
                i = int(data['opcounters']['insert'])
                u = int(data['opcounters']['update'])
                d = int(data['opcounters']['delete'])
                try:
                    qcpu = int(data['opcounters']['queryCpuTime'])
                    icpu = int(data['opcounters']['insertCpuTime'])
                    ucpu = int(data['opcounters']['updateCpuTime'])
                    dcpu = int(data['opcounters']['deleteCpuTime'])
                except KeyError:
                    qcpu = 0
                    icpu = 0
                    ucpu = 0
                    dcpu = 0
                con = int(data['connections']['current'])
              
                template="%12s%22s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s"
                header=('hostname', 'time', 'query', 'insert', 'update',  \
                        'delete', 'active con', 'resident', \
                        'virtual','mapped','load', 'bytesIn', 'bytesOut', 'numRequests', \
                        'queryCpu', 'insertCpu', 'updateCpu', 'deleteCpu')
                datastr="hostname, self.thetime(), (q-pq)/sleep, (i-pi)/sleep,(u-pu)/sleep, (d-pd)/sleep, con,  res, vir, mapd, self.getload(), bytesIn, bytesOut, numRequests, (qcpu-pqcpu)/sleep, (icpu-picpu)/sleep, (ucpu-pucpu)/sleep, (dcpu-pdcpu)/sleep"
      
            # opcounters will be in data if indexcounters is
            if "indexCounters" in data:
                idx_b_a = int(data['indexCounters']['btree']['accesses'])
                idx_b_h = int(data['indexCounters']['btree']['hits'])
                idx_b_m = int(data['indexCounters']['btree']['misses'])
                idx_b_o = round(float(data['indexCounters']['btree']['missRatio']),2)
                template="%12s%22s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s%12s"
                header=('hostname', 'time', 'query', 'insert', 'update',  \
                        'delete', 'active con', 'resident', \
                        'virtual','mapped','idx acc','idx hit','idx miss','idx ratio','load', 'bytesIn', 'bytesOut', 'numRequests', \
                        'queryCpu', 'insertCpu', 'updateCpu', 'deleteCpu')
                datastr="hostname, self.thetime(), (q-pq)/sleep, (i-pi)/sleep,(u-pu)/sleep, (d-pd)/sleep, \
                         con,  res, vir, mapd, (idx_b_a-pidx_b_a)/sleep, (idx_b_h-pidx_b_h)/sleep, (idx_b_m-pidx_b_m)/sleep, idx_b_o, self.getload(), bytesIn, bytesOut, numRequests, (qcpu-pqcpu)/sleep, (icpu-picpu)/sleep, (ucpu-pucpu)/sleep, (dcpu-pdcpu)/sleep"
                
            if (ii % 25 == 0):
                print template % header
            print template % (eval(datastr))
            deleted = int(data['metrics']['document']['deleted'])
            print("deleted = ", deleted)
           
            ii += 1
            
            time.sleep(sleep) 


if __name__ == "__main__":
    database="ycsb"
    hostname="localhost"
    port="27017"

    client = MongoClient("{}:{}".format(hostname, port))
    db = client.test
    stat = MongoStat(db)
    stat.printStats()

