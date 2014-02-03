#-*- coding:utf-8 -*-
from btdht import Parser

if __name__ == "__main__":
    parser=Parser.Parser('./torrents/5abfeb35aadeec51bb6bc124efe528e3a28f68c1.torrent')
    print parser.getName()
    print parser.getEncoding()
