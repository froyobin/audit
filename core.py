#!/usr/bin/python
import time
from offer_data import offer_instance_data
import offer_data
import audit_db
import string

HOST_IP='192.168.172.10'
USER='AuditUser'
PASSWD='1234'
PORT=3306
DB='audit_db'

class core_work:
    first = True
    def __init__(self):
        self.pre= offer_data.virtual_mach()

    def delinstance_to_db_prepare(self,new,old):
        i=0
        found=False
        for instance in new:
            if instance.instance_uuid == old[i].instance_uuid:
                i = i+1
                continue
            else:
                found=True
                break
        if found == True:
            detail = old[i]
            self.instance_need_handle(detail,"DELINS")
        else:
            self.instance_need_handle(old[-1],"DELINS")
    def instance_to_db_prepare(self,instance_info_list):
        #as new instance always add as the end of the list, so we need only handle the last one
        self.instance_need_handle(instance_info_list[-1],"ADDNEW")

    
    def instance_need_handle(self,instance_detail,cases):
        
        
        case_dic = {'ADDNEW':lambda :self.addnewinstance(instance_detail),\
                'UNKNOW':lambda :self.unknow(),\
                'DELINS':lambda :self.delins(instance_detail)}
        
        case_dic[cases]()

    def delins(self,detail):
        print detail.domain_name
    def addnewinstance(self,detail):
        store_list=[]
        store_list.append(detail.instance_uuid)
        store_list.append(detail.log_time)
        store_list.append(detail.cpu_time)
        store_list.append(detail.domain_name)
        store_list.append(detail.machine_state)
        store_list.append(detail.instance_memtotal)
        store_list.append(detail.instance_memcur)
        store_list.append(detail.cpu_num)
        store_list.append(detail.hardware[0][0].split(':')[1])
        store_list.append(detail.hardware[0][1].split(':')[1])
        #usage =  filter(str.isdigit,detail.cpu_num)
        #print usage
        store_list.append(detail.cpu_time)
        mydb = audit_db.auditDB(HOST_IP,USER,PASSWD,PORT,DB)
        mydb.store_in_db_static(store_list)
        mydb.disconnect()
        print "store_complete"

    def unknow(self):
        print "ERROR UNKNOW command"

    def check_instance_start_top(self,tmp,pre):
        if len(tmp.instance_info_list) > len(pre.instance_info_list):
            print "ADD"
            self.instance_to_db_prepare(tmp.instance_info_list)
        else:
            if len(tmp.instance_info_list) < len(pre.instance_info_list):
                self.delinstance_to_db_prepare(tmp.instance_info_list,pre.instance_info_list)
            
                print "DEC"
            else:
                #print tmp.instance_info_list[1].hardware[0][0].split(':')[1]
                print "OK"
        return

    def core_loop(self):
        #pre = offer_data.virtual_mach()
        while True:
            if self.first ==True:
                self.first = False
                pre = offer_instance_data()
                continue
            else:
                tmp = offer_instance_data()
                print "do something"
                """
                 do something
                """
                self.check_instance_start_top(tmp,pre)

                pre= tmp
            time.sleep(3)
if __name__ == '__main__':
    do_work = core_work()
    do_work.core_loop()
