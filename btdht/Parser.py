# -*- coding: utf-8 -*-
from .bencode import bdecode

class Parser(object):
    
    def __init__(self,filePath):
        self.path = filePath
        metainfo_file = open(str(self.path), 'rb')
        self.metainfo = bdecode(metainfo_file.read())
        #print self.metainfo
        metainfo_file.close()
    def getName(self):

        info = self.metainfo['info']

        if 'name.utf-8' in info:
            filename=info['name.utf-8']
        else:
            filename = info['name']

        for c in filename:
            if c=="'":
                filename=filename.replace(c,"\\\'")
        return filename

    def getEncoding(self):
        if 'encoding' in self.metainfo:
            return self.metainfo['encoding']
        return ""
    def getComments(self):
        info = self.metainfo['info']

        if 'comment.utf-8' in self.metainfo:
            comment=self.metainfo['comment.utf-8']
            return comment
        else:
            return ''