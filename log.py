#!/usr/bin/python
#-*- coding: utf8 -*-
import logging



class mylog:
    def __init__(self,filename):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(filename)
        self.fh.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)

        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh.setFormatter(self.formatter)
        self.ch.setFormatter(self.formatter)

        self.logger.addHandler(self.fh)
        #self.logger.addHandler(self.ch)
    def write_log(self,msg,level):
        case_dic = {'DEBUG':lambda :self.logger.debug(self,msg),\
                'INFO':lambda :self.logger.info(msg),\
                'WARNING':lambda :self.logger.warning(self,msg),\
                'ERROR':lambda :self.logger.error(self,msg),\
                'CRITICAL':lambda:self.logger.critical(self,msg)}
        
        case_dic[level]()



if __name__ == '__main__':
    m = mylog("test2.log")
    m.write_log("jell","INFO")
