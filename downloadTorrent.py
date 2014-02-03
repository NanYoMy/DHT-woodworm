# _*_ coding: utf-8 _*_
'''
    https://zoink.it
'''

import urllib,urllib2,os,MySQLdb,gzip
from io import BytesIO
from btdht import Parser

def save(filename, content):

    try:
        file = open(filename, 'wb')
        file.write(content)
        file.close()
    except IOError,e:
        print e

            

def getTorrents(info_hash):


    url="https://zoink.it/torrent/%s.torrent"%info_hash.upper()
    #url="http://torrage.com/torrent/%s.torrent"%info_hash.upper()
    #print url
    
    try:
        torrent=urllib2.urlopen(url,timeout=30)
        buffer = BytesIO(torrent.read())
        gz = gzip.GzipFile(fileobj=buffer)
        raw_data=gz.read()
        save(".\\torrents\\"+info_hash+".torrent",raw_data)
    except IOError,e:
        print e
        #print "downloading+"+info_hash+".torrent failed"
        return False
    #print "downloading+"+info_hash+".torrent success"
    return True

def getAllTorrents(table):

    try:
        os.mkdir("torrents")
    except WindowsError,e:
        print e

    try:
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='456',port=3306,charset="UTF8")
        cur=conn.cursor()
        conn.select_db('dht')
        sql="select * from "+table
        count=cur.execute(sql)
        print "thers are %s row in table"% count
        result=cur.fetchall()
        i=0
        for r in result:

            #the torrent info is empty
            if r[1]!="":
                print 'torrent exist'
                continue
            
            #download the torrent file success
            state=getTorrents(r[0])
            
            if state:
                #count the torrent file
                i=i+1

                try:
                    parser=Parser.Parser(".\\torrents\\"+r[0]+".torrent")
                except :
                    print 'bt file error'
                    
                name=parser.getName()
                print '============================================================='
                print r[0]
                #print name
                #update the tuple
                #print r[0]
                encoding=parser.getEncoding()
                comment=parser.getComments()
                #print comment.decode('utf-8')
                try:
                    
                    if encoding:
                        print name
                        print encoding
                        print name.decode(encoding)+" "+encoding
                        sql="update hash_info set hash_info.info='%s' where hash_info.hash='%s'"%(name.decode(encoding),r[0].decode('utf-8'))
                        #print sql
                        cur.execute(sql)
                    else:
                        print name
                        print name.decode('utf-8')+" "+encoding
                        sql="update hash_info set hash_info.info='%s' where hash_info.hash='%s'"%(name.decode('utf-8'),r[0].decode('utf-8'))
                        #print sql
                        cur.execute(sql)
                    conn.commit()
                except :
                    print 'mysql or decode error'
            else:
                try:
                    #torrent file download failed
                    sql="update hash_info set hash_info.info='%s' where hash_info.hash='%s'"%("error",r[0].decode('utf-8'))
                    cur.execute(sql)
                    conn.commit()
                except:
                    print 'error'
        
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print 'mysql error %d:%s'%(e.args[0],e.args[1])
        
    print 'the torrent files :'+str(i)    
if __name__=="__main__":

    getAllTorrents("hash_info")
'''
    info_hash="5302C30A88347F10E1F0A5BF334A8AC85D545AC0"
    getTorrents(info_hash)
'''
