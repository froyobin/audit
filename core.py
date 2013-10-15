#!/usr/bin/python
import time
from offer_data import offer_instance_data
import offer_data



class core_work:
    first = True
    def __init__(self):
        self.pre= offer_data.virtual_mach()

    def check_instance_start_top(self,tmp,pre):
        if len(tmp.instance_info_list) > len(pre.instance_info_list):
            add_instance_to_db
            print "ADD"
        else:
            if len(tmp.instance_info_list) < len(pre.instance_info_list):

                print "DEC"
            else:
                print "OK"
        return
    def core_loop(self):
        pre = offer_data.virtual_mach()
        while True:
            if self.first ==True:
                self.first = False
                pre = offer_instance_data()
                continue
            else:
                tmp = offer_instance_data()
                """
                 do something
                """
                self.check_instance_start_top(tmp,pre)

                pre= tmp
            time.sleep(3)
if __name__ == '__main__':
    do_work = core_work()
    do_work.core_loop()
