#!/usr/bin/python
import time
from offer_data import offer_instance_data
import offer_data
import audit_db
import sys
HOST_IP='192.168.172.10'
USER='AuditUser'
PASSWD='1234'
PORT=3306
DB='audit_db'
DEBUG=True
INSTANCE_MAX_NUM=256




class core_work:
    first = True
    def __init__(self):
        self.pre= offer_data.virtual_mach()
        self.ins_timestamp={}
    def removeinstance(self,instance):
        self.instance_need_handle(instance,"DELINS")
        self.disk_need_handle(instance,"DISCONNECT")
        self.net_need_handle(instance,"DISCONNECT")


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
                    self.removeinstance(old[i])
                    try:
                        del(self.ins_timestamp[old[i].instance_uuid])
                    except KeyError:
                        print "trying to del non-exist timestamp"
                        pass
                    old.remove(old[i])
            except IndexError:
                    self.removeinstance(old[i])
                    
                    
                    try:
                        print old[i].instance_uuid
                        del(self.ins_timestamp[old[i].instance_uuid])
                    except KeyError:
                        print "trying to del non-exist timestamp"
                        pass
                    
                    old.remove(old[i])


    def newaddinstance(self,instance,state):
        if state =="NEW":
            self.instance_need_handle(instance,"ADDNEW")
            self.disk_need_handle(instance,"ATTACHED")
            self.net_need_handle(instance,"ATTACHED")
        if state == "GENERAL":
            self.instance_need_handle(instance,"NORMAL")
            self.disk_need_handle(instance,"INUSE")
            self.net_need_handle(instance,"INUSE")



    def instance_to_db_prepare(self,instance_info_list,number):

        old = self.old
        new = self.new
        i=0
        while len(old) !=len(new):
            try:
                if old[i].instance_uuid == new[i].instance_uuid:
                    i = i+1
                    continue
                else:
                    self.newaddinstance(new[i],"NEW")
                    #self.ins_timestamp[new[i].instance_uuid]=time.time()
                    self.updatetime(new[i].instance_uuid)
                    old.insert(i,new[i])
                    
                
            except IndexError:
                    print "ADD",
                    self.newaddinstance(new[i],"NEW")
                    #self.ins_timestamp[new[i].instance_uuid]=time.time()
                    self.updatetime(new[i].instance_uuid)
                    old.append(new[i])

    
    def instance_need_handle(self,instance_detail,cases):
        
        
        case_dic = {'ADDNEW':lambda :self.handleinstance(instance_detail,5),\
                'UNKNOW':lambda :self.unknow(),\
                'NORMAL':lambda :self.handleinstance(instance_detail,1),\
                'DELINS':lambda :self.handleinstance(instance_detail,-1)}
        
        case_dic[cases]()

    

    
    def net_need_handle(self,detail,state):
        
        mydb = audit_db.auditDB(HOST_IP,USER,PASSWD,PORT,DB)
        i=0
        for card_names in detail.net_cards:
            store_list = []
            net_card_info = detail.net_card_info_list[i]
            store_list.append(detail.instance_uuid)
            store_list.append(detail.log_time)
            store_list.append(net_card_info[0]/1000)
            store_list.append(net_card_info[1])
            store_list.append(net_card_info[2])
            store_list.append(net_card_info[3])
            store_list.append(net_card_info[4]/1000)
            store_list.append(net_card_info[5])
            store_list.append(net_card_info[6])
            store_list.append(net_card_info[7])
            store_list.append(net_card_info[8]/1000)
            store_list.append(net_card_info[9]/1000)
            store_list.append(card_names['dev'])
            store_list.append(card_names['name'])
            store_list.append(state)
            """
            if state== "ATTACHED":
                store_list.append("ATTACHED")
            if state =="DISCONNECT":
                store_list.append("DISCONNECT")
            if state =="INUSE":
                store_list.append("INUSE")
            """
            mydb.store_in_db_net_state(store_list)
            if state == "ATTACHED":
                print " ADD NEW NET CARD %s into DATABASE SUCCESSFULLY"  % card_names['name']
            if state == "DISCONNECT":
                print "DISCONNECT NET CARD %s into DATABASE SUCCESSFULLY"  %card_names['name']
        mydb.disconnect()


    def disk_need_handle(self,detail,state):
       
        mydb = audit_db.auditDB(HOST_IP,USER,PASSWD,PORT,DB)
        #print detail.disk_stat
        for diskinfo in detail.disk_stat:
            store_list = []
            store_list.append(detail.instance_uuid)
            store_list.append((diskinfo['wr_total_times'])/1000000000L)
            store_list.append(diskinfo['rd_operations'])
            store_list.append((diskinfo['flush_total_times'])/10000L)
            store_list.append(diskinfo['rd_total_times']/10000L)
            store_list.append(diskinfo['rd_bytes']/1000L)
            store_list.append(diskinfo['flush_operations'])
            store_list.append(diskinfo['wr_operations'])
            store_list.append(diskinfo['wr_bytes']/1000L)
            store_list.append(diskinfo['diskname'])
            store_list.append(state)
            """
            if state== "ATTACHED":
                store_list.append("ATTACHED")
            if state =="DISCONNECT":
                store_list.append("DISCONNECT")
            if state =="INUSE":
                store_list.append("INUSE")
            """
            store_list.append(detail.log_time)
            mydb.store_in_db_disk_state(store_list)
            if state == 5:
                print "FIND NEW DISK %s into DATABASE SUCCESSFULLY"  % diskinfo['diskname']
            if state == -1:
                print "DISCONNECT DISK %s into DATABASE SUCCESSFULLY"  % diskinfo['diskname']
        mydb.disconnect()

    def handleinstance(self,detail,state):
        store_list=[]
        store_list.append(detail.instance_uuid)
        store_list.append(detail.log_time)
        store_list.append(detail.cpu_time)
        store_list.append(detail.domain_name)
        if state ==1:
            store_list.append(detail.machine_state)
        else:
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
        if state == 1:
            print "GENERAL INSTANCE %s LOG" % detail.instance_uuid

        
        




    def debug_log(self,msg):
        if DEBUG == True:
            sys.stdout.write(msg)
            sys.stdout.flush()


    def unknow(self):
        print "ERROR UNKNOW command"

    
    def loged_to_db(self,instance):
        self.newaddinstance(instance,"GENERAL")

    def updatetime(self,key):
        self.ins_timestamp[key]=time.time()
    
    def log_instance(self,key):
        update_list = self.new
        for instance in update_list:
            if instance.instance_uuid == key:
                self.loged_to_db(instance)
                
        self.updatetime(key)



    def expire_time_check(self,old,new):
        timenow = time.time()
        for (k,updatedtime) in self.ins_timestamp.items():
            if timenow-updatedtime >10:
                self.log_instance(k)
            else:
                print "not now"
                continue

    def inspect_each_instance(self,old,new):
        
        self.expire_time_check(old,new)



    def check_instance_start_stop(self,tmp,pre):
        if len(self.new) > len(self.old):
            number = len(self.new) - len(self.old)
            self.instance_to_db_prepare(tmp.instance_info_list,number)
        else:
            if len(self.new) < len(self.old):
                print "DEC"
                self.delinstance_to_db_prepare()
            else:
                self.inspect_each_instance(self.old,self.new)
                #print tmp.instance_info_list[1].hardware[0][0].split(':')[1]
                #tmp = self.old.instance_info_list[:]
                #tmp = self.new.instance_info_list[:]
                #self.debug_log("do something")
        return
    
    def create_timestamp(self):
        for instance in self.old:
            self.ins_timestamp[instance.instance_uuid] = time.time()
    def core_loop(self):
        #pre = offer_data.virtual_mach()
        while True:
            if self.first ==True:
                self.first = False
                pre = offer_instance_data()
                self.old = pre.instance_info_list
                self.create_timestamp()
                continue
            else:
                tmp = offer_instance_data()
                self.new = tmp.instance_info_list
                
                """
                 do something
                """
                self.check_instance_start_stop(tmp,pre)

                pre= tmp
            time.sleep(2)
if __name__ == '__main__':
    do_work = core_work()
    do_work.core_loop()
