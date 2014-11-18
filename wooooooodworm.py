#_*_ coding: utf-8 _*_
__author__ = 'NanYoMy'
import logging
import time
from conf import *
from btdht import DHT
from btdht import Parser


if __name__ == "__main__":

    # Enable logging
    stdLogLevel = logging.ERROR
    fileLogLevel = logging.DEBUG

    #formatter = logging.Formatter("[%(levelname)s@%(created)s] %(message)s")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("HASH.log")
    file_handler.setFormatter(formatter)

    logging.getLogger("btdht").setLevel(fileLogLevel)
    logging.getLogger("btdht").addHandler(file_handler)
    logging.getLogger("std").setLevel(stdLogLevel)
    logging.getLogger("std").addHandler(stdout_handler)
    #thread number
    threadNumb=THREAD_NUMBER
    #working time for threads
    workingTime=WORKINGTIME
    #threads pool
    threads=[]
    for i in xrange(threadNumb):
        i=i+9500
        thread = DHT(host='0.0.0.0', port=i)
        thread.start()
        thread.bootstrap('router.bittorrent.com',6881)
        CurrentMagnet = "4CDE5B50A8930315B479931F6872A3DB59575366"
        thread.ht.add_hash(CurrentMagnet.decode("hex"))
        threads.append(thread)
        print "start node %d"%i
        #time.sleep(2)

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
