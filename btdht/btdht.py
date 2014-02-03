# -*- coding: utf-8 -*-

import SocketServer
import socket
import threading
import time
import logging
import re
import urllib2

from .defines import *
from .rtable import RoutingTable
from .htable import HashTable
from .bencode import bdecode, BTFailure
from .node import Node
from .utils import decode_nodes, encode_nodes, random_node_id, unpack_host, unpack_hostport


logger = logging.getLogger(__name__)

class DHTRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        logger.debug("Got packet from: %s:%d" % (self.client_address))
        if self.server.dht.node.LANip == self.client_address[0]:
            #print "self request"
            return

        req = self.request[0].strip()

        try:
            message = bdecode(req)
            msg_type = message["y"]
            logger.debug("This is DHT connection with msg_type: %s" % (msg_type))

            if msg_type == "r":
                self.handle_response(message)
            elif msg_type == "q":
                self.handle_query(message)
            elif msg_type == "e":
                self.handle_error(message)
            else:
                logger.error("Unknown rpc message type %r" % (msg_type))
        except BTFailure:
            logger.error("Fail to parse message %r" % (self.request[0].encode("hex")))
            pass

    #处理clients对我们的response
    def handle_response(self, message):
        trans_id = message["t"]
        args = message["r"]
        node_id = args["id"]

        client_host, client_port = self.client_address
        logger.debug("Response message from %s:%d, t:%r, id:%r" % (client_host, client_port, trans_id.encode("hex"), node_id.encode("hex")))

        # Do we already know about this node?
        node = self.server.dht.rt.node_by_id(node_id)
        if not node:
            logger.debug("Cannot find appropriate node during simple search: %r" % (node_id.encode("hex")))
            # Trying to search via transaction id
            #get the node who sent the request, that correspondents to the response
            node = self.server.dht.rt.node_by_trans(trans_id)
            if not node:
                logger.debug("Cannot find appropriate node for transaction: %r" % (trans_id.encode("hex")))
                return

        logger.debug("We found apropriate node %r for %r" % (node, node_id.encode("hex")))

        if trans_id in node.trans:
            logger.debug("Found and deleting transaction %r in node: %r" % (trans_id.encode("hex"), node))
            #由于长时间没有响应的node会被自动删除,这里关系到多线程并发。所以可能会有bug
            #the server thread competes "node" resource with the iterative_thread
            try:
                trans = node.trans[trans_id]
                node.delete_trans(trans_id)
            except:
                logger.debug('delete trans on a deleted node')
                return
        else:
            logger.debug("Cannot find transaction %r in node: %r" % (trans_id.encode("hex"), node))
            '''
            for trans in node.trans:
                logger.debug(trans.encode("hex"))
            return
            '''
            return

        if "ip" in args:
            logger.debug("They try to SECURE me: %s", unpack_host(args["ip"].encode('hex')))

        #the server thread competes "node" resource with the iterative_thread
        try:
            t_name = trans["name"]
        except:
            logger.debug('get name on a deleted trans')
            return
        
        
        if t_name == "find_node":
            node.update_access()
            logger.debug("find_node response from %r" % (node))
            if "nodes" in args:
                new_nodes = decode_nodes(args["nodes"])
                logger.debug("We got new nodes from %r" % (node))
                for new_node_id, new_node_host, new_node_port in new_nodes:
                    logger.debug("Adding %r %s:%d as new node" % (new_node_id.encode("hex"), new_node_host, new_node_port))
                    self.server.dht.rt.update_node(new_node_id, Node(new_node_host, new_node_port, new_node_id))

            # cleanup boot node
            if node._id == "boot":
                logger.debug("This is response from \"boot\" node, replacing it")
                # Create new node instance and move transactions from boot node to newly node
                new_boot_node = Node(client_host, client_port, node_id)
                new_boot_node.trans = node.trans
                self.server.dht.rt.update_node(node_id, new_boot_node)
                # Remove old boot node
                self.server.dht.rt.remove_node(node._id)
        elif t_name == "ping":
            #update the node if it can pong us!!!
            node.update_access()
            logger.debug("ping response for: %r" % (node))
        elif t_name == "get_peers":

            node.update_access()
            info_hash = trans["info_hash"]
            logger.debug("get_peers response for %r" % (node))
            if "token" in args:
                token = args["token"]
                logger.debug("Got token: %s" % (token.encode("hex")))
            else:
                token = None
                #logger.error(self.server.dht.name+" No token in get_peers response from %r" % (node))
            if "values" in args:
                logger.debug("We got new peers for %s" % (info_hash.encode("hex")))
                values = args["values"]
                for addr in values:
                    hp = unpack_hostport(addr)
                    self.server.dht.ht.add_peer(info_hash, hp)
                    logger.debug("Got new peer for %s: %r" % (info_hash.encode("hex"), hp))
            if "nodes" in args:
                logger.debug("We got new nodes from %r" % (node))
                new_nodes = decode_nodes(args["nodes"])
                for new_node_id, new_node_host, new_node_port in new_nodes:
                    logger.debug("Adding %r %s:%d as new node" % (new_node_id.encode("hex"), new_node_host, new_node_port))
                    self.server.dht.rt.update_node(new_node_id, Node(new_node_host, new_node_port, new_node_id))
        '''
        here we do not annouce a peer, so we needn't implement the code for a "announce peer" message
        '''

    #处理clients对我们的query
    def handle_query(self, message):
        trans_id = message["t"]
        query_type = message["q"]
        args = message["a"]
        node_id = args["id"]

        client_host, client_port = self.client_address
        logger.debug(self.server.dht.name+" Query message %s from %s:%d, id:%r" % (query_type, client_host, client_port, node_id.encode("hex")))
        
        # Do we know already know about this node?
        node = self.server.dht.rt.node_by_id(node_id)
        if not node:
            node = Node(client_host, client_port, node_id)
            logger.debug("We don`t know about %r, add it as new" % (node))
            self.server.dht.rt.update_node(node_id, node)
        else:
            logger.debug("We already know about: %r" % (node))

        node.update_access()

        if query_type == "ping":
            logger.debug("handle query ping")
            node.pong(socket=self.server.socket, trans_id = trans_id, sender_id=self.server.dht.node._id, lock=self.server.send_lock)
            logger.debug(self.server.dht.name+" handle query ping from %s"% node.host)
        elif query_type == "find_node":
            logger.debug("handle query find_node")
            logger.debug(self.server.dht.name+" handle query find_node %s"% node.host)
            target = args["target"]
            #获取最近的8个node

            #tmpNodes=dict(self.server.dht.rt.get_close_nodes(target, 7))
            #tmpNodes[self.server.dht.node._id]=self.server.dht.node
            #tmpNodes=dict(self.server.dht.rt.get_close_nodes(target, 7).items())
            #tmpNodes[self.server.dht.node._id]=self.server.dht.node
            tmpNodes=[(self.server.dht.node._id,self.server.dht.node)]
            #aha return myself it's trick
            '''
            tmpNodes.append(self.server.dht.rt.sample(1))
            tmpNodes.append(self.server.dht.node)
            found_nodes = encode_nodes(tmpNodes)
            '''
            found_nodes = encode_nodes(tmpNodes)
            node.found_node(found_nodes, socket=self.server.socket, trans_id = trans_id, sender_id=self.server.dht.node._id, lock=self.server.send_lock)
        elif query_type == "get_peers":
            logger.debug("handle query get_peers")
            node.pong(socket=self.server.socket, trans_id = trans_id, sender_id=self.server.dht.node._id, lock=self.server.send_lock)

            #todo get hash_info
            self.server.dht.ht.add_hash(args["info_hash"])
            #translate the ASCII into hex
            logger.debug(self.server.dht.name+" handle query get_peers %s from host:%s"%(args["info_hash"].encode('hex'),node.host))

            return
        elif query_type == "announce_peer":

            logger.debug("handle query announce_peer")
            node.pong(socket=self.server.socket, trans_id = trans_id, sender_id=self.server.dht.node._id, lock=self.server.send_lock)

            #todo get hash_info
            self.server.dht.ht.add_hash(args["info_hash"])
            #translate the ASCII into hex
            logger.debug(self.server.dht.name+" handle query announce_peer %s from host:%s"%(args["info_hash"].encode('hex'),node.host))

            return
        else:
            logger.error(self.server.dht.name+" Unknown query type: %s" % (query_type))

    def handle_error(self, message):
        logger.debug("We got error message from: ")
        return
'''
the DHTServer is derived from the SocketServer.UDPServer and SocketServer.ThreadingMixIn
for each request, the DHTServer will create a thread to responce it, for it derived from ThreadingMixIn
'''
class DHTServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    def __init__(self, host_address, handler_cls):
        #__init__ is the constructor of the UDPServer
        SocketServer.UDPServer.__init__(self, host_address, handler_cls)
        #the mutex for multi_threading
        self.send_lock = threading.Lock()

class DHT(threading.Thread):


    def __init__(self, host, port):


        threading.Thread.__init__(self)
        #constructor a node by its port,id,ip
        id=random_node_id()
        print id.encode('hex')
        self.node = Node(unicode(host), port, id)
        self.rt = RoutingTable()
        self.ht = HashTable()
        #(self.node.host, self.node.port):host_address
        #handler_cls:DHTRequestHandler
        self.server = DHTServer((self.node.host, self.node.port), DHTRequestHandler)
        self.server.dht = self
        self.sample_count = SAMPLE_COUNT
        self.max_bootstrap_errors = MAX_BOOTSTRAP_ERRORS
        self.iteration_timeout = ITERATION_TIMEOUT
        self.gc_max_time = GC_MAX_TIME
        self.gc_max_trans = GX_MAX_TRANS
        self.randomize_node_id = RANDOMIZE_NODE_ID
        self.random_find_peers = RANDOM_FIND_PEERS
        self.running = False
        logger.debug("DHT Server listening on %s:%d" % (host, port))
        #create a thread, it will help us the deal the requests with multi-threading.
        #we didn't start it here!!!!
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        #把他设置为后台进程。
        self.server_thread.daemon = True
        #迭代地去find_node
        #we start it here!!!!
        self.iterative_thread = threading.Thread(target=self.iterative)
        self.iterative_thread.daemon = True

    def run(self):

        self.server_thread.start()
        logger.debug("DHT server thread started")
        self.bootstrap('router.bittorrent.com',6881)
        #self.bootstrap('router.bitcomet.net',554)
        CurrentMagnet = "4CDE5B50A8930315B479931F6872A3DB59575366"
        self.ht.add_hash(CurrentMagnet.decode("hex"))

    def bootstrap(self, boot_host, boot_port):
        logger.debug("Starting DHT bootstrap on %s:%d" % (boot_host, boot_port))
        boot_node = Node(boot_host, boot_port, "boot")
        #the boot node is also a node in our router table
        self.rt.update_node("boot", boot_node)
        # Do cycle, while we didnt get enough nodes to start
        while self.rt.count() <= self.sample_count:

            if len(boot_node.trans) > self.max_bootstrap_errors:
                logger.error("Too many attempts to bootstrap, seems boot node %s:%d is down. Givin up" % (boot_host, boot_port))
                return False

            #去find自己，这样的作用是可以得到与自己邻近的节点
            #self.server.socket是UDP的socket
            boot_node.find_node(self.node._id, socket=self.server.socket, sender_id=self.node._id)
            time.sleep(self.iteration_timeout)

        self.running = True
        self.iterative_thread.start()
        return True

    def iterative(self):
        logger.debug("Entering iterative node finding loop")

        while self.running:

            # find nodes
            if self.randomize_node_id:
                nid = random_node_id()
                #随机抽取sample_count个nodes
                nodes = self.rt.sample(self.sample_count)
            else:
                nid = self.node._id
                nodes = self.rt.get_close_nodes(nid, self.sample_count)

            for node_id, node in nodes:
                #通过这个node寻找
                '''
                print node_id.encode('hex')
                print nid.encode('hex')
                '''
                node.find_node(nid, socket=self.server.socket, sender_id=self.node._id)
                #print "make friend"
            # garbage collector
            nodes = self.rt.sample(int(self.rt.count() / 2))
            #nodes = self.rt.get_nodes().items()

            for node_id, node in nodes:
                time_diff = time.time() - node.access_time
                if time_diff > self.gc_max_time:
                    if len(node.trans) > self.gc_max_trans:
                        logger.debug("We have node with last access time difference: %d sec and %d pending transactions, remove it: %r" % (time_diff, len(node.trans), node))
                        self.rt.remove_node(node_id)
                        continue
                    node.ping(socket=self.server.socket, sender_id=self.node._id)

            # peer search
            for hash_id in self.ht.hashes.keys():
                if self.random_find_peers:
                    nodes = self.rt.sample(self.sample_count)
                else:
                    nodes = self.rt.get_close_nodes(hash_id, self.sample_count)
                for node_id, node in nodes:
                    node.get_peers(hash_id, socket=self.server.socket, sender_id=self.node._id)
                   # print "get peers"

            time.sleep(self.iteration_timeout)

    def stop(self):

        #stop the iterative method
        self.running = False
        #synchronize the thread
        self.iterative_thread.join()
        logger.debug("Stopped iterative loop")
        #synchronize the thread
        self.server.shutdown()
        self.server_thread.join()
        self.ht.closeDataBase()
        logger.debug("Stopped server thread")
           
