#-*- coding:utf-8 -*-
import MySQLdb
import os

def createDatabase():
    try:
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='456',port=3306,charset="UTF8")
        cur=conn.cursor()
        cur.execute('create database if not exists dht')
        conn.select_db('dht')
        cur.execute('drop table if exists hash_info')
        cur.execute('drop table if exists peerIP')
        cur.execute('create table hash_info(hash varchar(40), info varchar(100),primary key(hash))')
        cur.execute('create table peerIP(ip varchar(40), info varchar(100),primary key(ip))')
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print 'mysql error %d:%s'%(e.args[0],e.args[1])

def insertInfo(hash):
    try:
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='456',port=3306,charset="UTF8")
        cur=conn.cursor()
        conn.select_db('dht')
        sql="insert into hash_info(hash,info) values('%s','%s')"%(hash,"the info will added later")
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print 'mysql error %d:%s'%(e.args[0],e.args[1])

def selectAllTable(table):
    try:
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='456',port=3306,charset="UTF8")
        cur=conn.cursor()
        conn.select_db('dht')
        sql="select * from "+table
        count=cur.execute(sql)
        print "thers are %s row in table:"% count
        result=cur.fetchall()
        
        for r in result:
            #print 'magnet:?xt=urn:btih:'+r[0].upper()+" info:"+r[1]
            if r[1]!="error" and r[1]!="":
                print r[1]
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print 'mysql error %d:%s'%(e.args[0],e.args[1])

def executeSQL(sql):
    try:
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='456',port=3306,charset="UTF8")
        cur=conn.cursor()
        conn.select_db('dht')
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print 'mysql error %d:%s'%(e.args[0],e.args[1])



#sql="update hash_info set hash_info.info='Captain's VgHD DVD 21 a0472 to a0501.iso' where hash_info.hash='5302c42cdf439cafa98f048e8367b3ff4829628e'".encode('utf-8')
#print sql
#executeSQL(sql)
#createDatabase()       
#insertInfo("4cde5b50a8930315b479931f6872a3db59575366")
selectAllTable("hash_info")
#selectAllTable("peerIP")
