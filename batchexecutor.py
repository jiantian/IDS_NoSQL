from copy import deepcopy
from threading import Thread, Condition
from tempfile import NamedTemporaryFile
from os import system, remove
from time import sleep
from re import compile

class ClassifierFlags:
    TrainNormal, TrainAnomaly, Test = range(3)

class BatchExecutor (Thread):
    def __init__(self, batchfile, detectionalgorithm, doperceptronlearn,
                 hostname='localhost', port=27017, sleeptime=0.0):
        super(BatchExecutor, self).__init__()
        self.batchfile = batchfile
        self.detectionalgorithm = detectionalgorithm
        self.doperceptronlearn = doperceptronlearn
        self.hostname = hostname
        self.port = port
        self.sleeptime = sleeptime
        self.measurecv = Condition()
        self.measuringDone = True
        self.allMeasuringDone = False
        self.measuringFailure = False
        self.trainTime = 0.0
        self.classifierData = ''
    
    def signal_measuring_ready_or_all_done(self, allDone):
        self.measurecv.acquire()
        self.measuringDone = False
        self.allMeasuringDone = allDone
        self.measurecv.notify_all()
        self.measurecv.release()
    
    def signal_measuring_failed(self):
        self.measurecv.acquire()
        self.measuringFailure = True
        self.measurecv.notify_all()
        self.measurecv.release()
    
    def signal_measuring_done(self, classifierData, duration):
        self.measurecv.acquire()
        self.measuringDone = True
        self.classifierData = classifierData
        self.trainTime = duration
        self.measurecv.notify_all()
        self.measurecv.release()
    
    def wait_for_measure_to_be_ready_all_done_or_failed(self):
        self.measurecv.acquire()
        while self.measuringDone and not self.measuringFailure:
            self.measurecv.wait()
        allDoneStatus = self.allMeasuringDone
        ret = self.trainTime if not self.measuringFailure else None
        self.measurecv.release()
        return allDoneStatus, ret
    
    def wait_for_measure_to_finish(self):
        self.measurecv.acquire()
        while not self.measuringDone:
            self.measurecv.wait()
        # deep copy classifier data to avoid data races
        classifierData = deepcopy(self.classifierData)
        duration = self.trainTime
        self.measurecv.release()
        return classifierData, duration
    
    def run_batch(self, file_object, train_time, classifier_mode,
        query_executed, expression):
        if classifier_mode == None:
            if not file_object == None:
                file_object.close()
            self.signal_measuring_failed()
            return False
        if not query_executed:
            done = train_time <= 0
            if not done:
                tf = NamedTemporaryFile(mode='w+', suffix='.js', delete=False)
                filename = tf.name
                tf.write(expression)
                tf.close()
            
            while not done:
                self.signal_measuring_ready_or_all_done(False)
                system("mongo --host {} --port {} db {}".format(
                    self.hostname, self.port, filename))
                sleep(self.sleeptime)
                data, duration = self.wait_for_measure_to_finish()
                done = duration <= 0
                
                remove(filename)
                
                query_executed = True
                if classifier_mode == ClassifierFlags.TrainNormal:
                    print "Training as normal..."
                    self.detectionalgorithm.trainSet.append({data:'Normal'})
                    self.detectionalgorithm.size_normal_train += 1
                elif classifier_mode == ClassifierFlags.TrainAnomaly:
                    print "Training as anomaly..."
                    self.detectionalgorithm.trainSet.append({data:'Anomaly'})
                    self.detectionalgorithm.size_anomaly_train += 1
                else:
                    print "Testing..."
                    if self.doperceptronlearn == True:    
                        self.detectionalgorithm.preProcess()
                        self.doperceptronlearn = False
                    try:
                        label = self.detectionalgorithm.getLabel(data)
                    except:
                        label = "<Error>"
        
                if classifier_mode == ClassifierFlags.Test:
                    print label
        return True
    
    def run(self):
        classifier_mode = None
        query_executed = True
        expression = ""
        theTrainTime = 0.0
        firstRun = True
        failure = False
        with open(self.batchfile, 'r') as f:
            for line in f:
                pat = compile('^\$\$([^\s\(]*)\s*((\d+(.\d*)?)|(.\d+))\$\$$')
                matches = pat.match(line)
                if matches != None and len(matches.groups()) >= 3:
                    if firstRun:
                        firstRun = False
                    elif not self.run_batch(f, theTrainTime, classifier_mode,
                        query_executed, expression):
                        failure = True
                    if not failure:
                        expression = ""
                        classType = matches.group(1)
                        theTrainTime = self.trainTime = float(matches.group(2))
                        if classType == "normal":
                            classifier_mode = ClassifierFlags.TrainNormal
                        elif classType == "anomaly":
                            classifier_mode = ClassifierFlags.TrainAnomaly
                        elif classType == "test":
                            classifier_mode = ClassifierFlags.Test
                elif firstRun:
                    f.close()
                    self.signal_measuring_failed()
                    failure = True
                else:
                    query_executed = False
                    expression += line
                if failure:
                    break
        if not failure and self.run_batch(None, theTrainTime, classifier_mode,
                                          query_executed, expression):
            self.signal_measuring_ready_or_all_done(True)
