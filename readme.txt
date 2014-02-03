this python(2.7.1) program is attended to get the magnet URIs from DHT network.also it need MySQL to maintain the magnet URIs.

HOW TO RUN THE PROGRAM

0.working on window7
1.install python 2.7.1
2.install mysql (set the charset to utf-8)
3.install the connector betweent python and mysql "the connector can download from www.python.org"
4.run the "mysql.py" to create database(set the "passwd" ,"user"and "port" by your own condition)
5.run the "wooooooodworm.py" to get magnet URI from network (set the "threadNumb" and "workingTime" by yourself)
6.run the "downloadTorrent.py" to get the torrnet file from the "zoink.it"(set the "passwd" ,"user"and "port" on your own condition)
7.check the "./torrents" file, it contains the torrents that you get from network.
8.check the database table "hash_info",it maintain the magnet info that you get from network 