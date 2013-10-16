#!/usr/bin/python
import time
from offer_data import offer_instance_data
import offer_data
import audit_db
HOST_IP='192.168.172.10'
USER='AuditUser'
PASSWD='1234'
PORT=3306
DB='audit_db'

class core_work:
    first = True
    def __init__(self):
        self.pre= offer_data.virtual_mach()

    def delinstance_to_db_prepare(self):
        i=0
        old = self.old
        new = self.new
        ###WATCH OUT!!!! as this algorithm only consider that at this moment only some 
        ### instances are removed and no instances add at this moment
        ### the extream condition is that at this sample time some instance are created and some are removed!!
        ### like old: 1 3 6 7 and new :1 3 8 . we remove 6 and 7 but add a new instance 8
        while len(old) != len(new):
            try:
                if old[i].instance_uuid == new[i].instance_uuid:
                    i = i+1
                    continue
                else:
                    self.instance_need_handle(old[i],"DELINS")
                    old.remove(old[i])
                    #print len(old)
                    #print len(new)
            except IndexError:
                    #print i
                    self.instance_need_handle(old[i],"DELINS")
                    old.remove(old[i])



                #self.instance_need_handle(old[-1],"DELINS")
    def instance_to_db_prepare(self,instance_info_list,number):
        #print "*************all**************"
        #for ins in self.new:
        #    print ins.instance_uuid
        #print "*****************************"
        #print number
        #print "**********ADDDE**************"
        #for i in range(0,number):
            #self.instance_need_handle(instance_info_list[-1-i],"ADDNEW")
        #    print self.new[-1-i].instance_uuid
        #print "********************************"

        #print "FINISH"
        #we should put the new instances in the end of old one pretending it is existed!!
        #for i in range(0,number):     
        #    self.old.append(instance_info_list[-1-i])
        old = self.old
        new = self.new
        i=0
        while len(old) !=len(new):
            try:
                if old[i].instance_uuid == new[i].instance_uuid:
                    i = i+1
                    continue
                else:
                    self.instance_need_handle(new[i],"ADDNEW")
                    old.insert(i,new[i])
                
            except IndexError:
                    print "ADD"
                    print i
                    self.instance_need_handle(new[i],"ADDNEW")
                    old.append(new[i])
                    #old.remove(old[i])
                    #print "report except"
                    #print i

    
    def instance_need_handle(self,instance_detail,cases):
        
        
        case_dic = {'ADDNEW':lambda :self.handleinstance(instance_detail,5),\
                'UNKNOW':lambda :self.unknow(),\
                'DELINS':lambda :self.handleinstance(instance_detail,-1)}
        
        case_dic[cases]()

        
    def handleinstance(self,detail,state):
        store_list=[]
        store_list.append(detail.instance_uuid)
        store_list.append(detail.log_time)
        store_list.append(detail.cpu_time)
        store_list.append(detail.domain_name)
        #store_list.append(detail.machine_state)
        store_list.append(state)
        store_list.append(detail.instance_memtotal)
        store_list.append(detail.instance_memcur)
        store_list.append(detail.cpu_num)
        store_list.append(detail.hardware[0][0].split(':')[1])
        store_list.append(detail.hardware[0][1].split(':')[1])
        store_list.append(detail.cpu_time)
        mydb = audit_db.auditDB(HOST_IP,USER,PASSWD,PORT,DB)
        mydb.store_in_db_static(store_list)
        mydb.disconnect()
        if state == 5:
            print "ADD NEW INSTANCE %s into DATABASE SUCCESSFULLY"  % detail.domain_name
        if state == -1:
            print "TERMINATE INSTANCE %s into DATABASE SUCCESSFULLY"  % detail.domain_name

        
        






    def unknow(self):
        print "ERROR UNKNOW command"

    def check_instance_start_top(self,tmp,pre):
        if len(self.new) > len(self.old):
            number = len(self.new) - len(self.old)
            self.instance_to_db_prepare(tmp.instance_info_list,number)
        else:
            if len(self.new) < len(self.old):
                self.delinstance_to_db_prepare()
            
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
                self.old = pre.instance_info_list
                print self.first
                continue
            else:
                tmp = offer_instance_data()
                self.new = tmp.instance_info_list
                print "do something"
                """
                 do something
                """
                self.check_instance_start_top(tmp,pre)

                pre= tmp
            time.sleep(2)
if __name__ == '__main__':
    do_work = core_work()
    do_work.core_loop()
