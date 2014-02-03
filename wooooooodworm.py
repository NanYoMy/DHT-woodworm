#_*_ coding: utf-8 _*_
__author__ = 'NanYoMy'
import logging
import time
from btdht import DHT
from btdht import Parser


if __name__ == "__main__":

    # Enable logging
    loglevel = logging.ERROR
    formatter = logging.Formatter("[%(levelname)s@%(created)s] %(message)s")
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    logging.getLogger("btdht").setLevel(loglevel)
    logging.getLogger("btdht").addHandler(stdout_handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)
    logger.addHandler(stdout_handler)
    #thread number
    threadNumb=5
    #working time for threads
    workingTime=60*60*6
    #threads pool
    threads=[]
    for i in xrange(threadNumb):
        print i+9500
        #thread = DHT(host='192.168.1.101', port=i)
        thread = DHT(host='0.0.0.0', port=i)
        thread.start()
        threads.append(thread)
        time.sleep(5)

    time.sleep(workingTime)

    for i in threads:
        print "stop thread "+i.name
        i.stop()
        i.join()
        #i.rt.saveAllPeer(i.name)
        #i.ht.saveHashInfo(i.name)
        i.rt.nodes.clear()
        i.ht.hashes.clear()
        print 'finish thread'+i.name

    
'''
    dht.ht.hashes.clear()
    dht.rt.nodes.clear()
'''
